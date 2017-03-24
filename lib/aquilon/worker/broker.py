# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016  Contributor
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Module containing the base class BrokerCommand """

import sys
from inspect import isclass
from types import NoneType

from sqlalchemy import event
from sqlalchemy.sql import text
from sqlalchemy.exc import DatabaseError
from twisted.web import http
from twisted.python import log

from aquilon.config import Config
from aquilon.exceptions_ import (ArgumentError, AuthorizationException,
                                 NotFoundException, UnimplementedError,
                                 PartialError, AquilonError, TransientError)
from aquilon.worker.exporter import Exporter
from aquilon.worker.authorization import AuthorizationBroker
from aquilon.worker.messages import StatusCatalog
from aquilon.worker.logger import RequestLogger
from aquilon.aqdb.db_factory import DbFactory
from aquilon.aqdb.model.xtn import start_xtn, end_xtn
from aquilon.worker.formats.formatters import ResponseFormatter
from aquilon.worker.dbwrappers.user_principal import (
    get_or_create_user_principal)
from aquilon.locks import LockKey
from aquilon.worker.templates.base import Plenary, PlenaryCollection
from aquilon.worker.templates.domain import TemplateDomain
from aquilon.worker.services import Chooser
from aquilon.worker.dbwrappers.branch import sync_domain

# Things we don't need cluttering up the transaction details table
_IGNORED_AUDIT_ARGS = ('requestid', 'bundle', 'debug', 'session', 'dbuser')

# Mapping of command exceptions to client return code.
ERROR_TO_CODE = {NotFoundException: http.NOT_FOUND,
                 AuthorizationException: http.UNAUTHORIZED,
                 ArgumentError: http.BAD_REQUEST,
                 UnimplementedError: http.NOT_IMPLEMENTED,
                 PartialError: http.MULTI_STATUS,
                 TransientError: http.SERVICE_UNAVAILABLE}


def get_code_for_error_class(e):
    if e is None or e is NoneType:
        return http.OK
    return ERROR_TO_CODE.get(e, http.INTERNAL_SERVER_ERROR)


class BrokerCommand(object):
    """ The basis for each command module under commands.

    Several class-level lists and flags are defined here that can be
    overridden on a per-command basis.  Some can only be overridden
    in __init__, though, so check the docstrings.

    """

    required_parameters = []
    """ This will generally be overridden in the command class.

    It could theoretically be parsed out of input.xml, but that is
    tricky in some cases and possibly error-prone.

    """

    optional_parameters = []
    """ Optional parameters are filled in automatically from input.xml.

    This may contain entries that are also in the required_parameters list.
    If so, the required entry "wins".

    """

    requires_transaction = True
    """ This sets up a session and cleans up when finished.

    Currently, setting azcheck to True will force this value to be True,
    because the azcheck requires a session that will need to be cleaned
    up.

    """

    requires_plenaries = False
    """ Causes the plenary management machinery to be initialized.
    """

    requires_format = None
    """ Run command results through the formatter.

    It is automatically set to True for all cat, search, and show
    commands, but could be reversed back to False by overriding __init__
    for the command.

    """

    requires_readonly = False
    """ Require read only isolation level for the render session.

    It is automatically set to True for all search and show commands,
    but could be reversed back to False by overriding __init__ for the
    command.

    """

    # Override to indicate whether the command will generally take a
    # lock during execution.
    #
    # Any command with this flag set to True will use the separate
    # NLSession thread pool and should not have to wait on commands
    # that are potentially all blocking on the same lock.
    #
    # If set to None (the default), the is_lock_free property will
    # examine the command's module to try to determine if a lock
    # may be required and then cache the value.
    _is_lock_free = None

    # Run the render method on a separate thread.  This will be forced
    # to True if requires_transaction.
    defer_to_thread = True

    def __init__(self):
        """ Provides some convenient variables for commands.

        Also sets requires_* parameters for some sets of commands.
        All of the command objects are singletons (or Borg).

        """
        self.dbf = DbFactory()
        self.config = Config()
        self.az = AuthorizationBroker()
        self.formatter = ResponseFormatter()
        self.catalog = StatusCatalog()
        # Force the instance to have local copies of the class defaults...
        # This allows resources.py to modify instances without worrying
        # about inheritance issues (classes sharing required or optional
        # parameters).
        self.required_parameters = self.required_parameters[:]
        self.optional_parameters = self.optional_parameters[:]

        self.action = self.__module__
        package_prefix = "aquilon.worker.commands."
        if self.action.startswith(package_prefix):
            self.action = self.action[len(package_prefix):]
        # self.command is set correctly in resources.py after parsing input.xml
        self.command = self.action

        # Simplify the initialization of common command categories
        if self.action.startswith("show") or \
           self.action.startswith("search") or \
           self.action.startswith("cat"):
            self.requires_readonly = True

        if not self.defer_to_thread:
            if self.requires_transaction:  # pragma: no cover
                self.defer_to_thread = True
                log.msg("Forcing defer_to_thread to True because of "
                        "required authorization or transaction for %s" %
                        self.command)
        # free = "True " if self.is_lock_free else "False"
        # log.msg("is_lock_free = %s [%s]" % (free, self.command))

    def audit_result(self, session, key, value, **arguments):
        # We need a place to store the result somewhere until we can finish the
        # audit record. Use the request object for now.
        request = arguments["request"]
        if not hasattr(request, "_audit_result"):
            request._audit_result = []

        request._audit_result.append((key, value))

    def render(self, **_):  # pragma: no cover
        """ Implement this method to create a functional broker command.

        The base __init__ method wraps all implementations using
        invoke_render() to enforce the class requires_* flags.

        """
        if self.__class__.__module__ == 'aquilon.worker.broker':
            # Default class... no useful command info to repeat back...
            raise UnimplementedError("Command has not been implemented.")
        raise UnimplementedError("%s has not been implemented" %
                                 self.__class__.__module__)

    def invoke_render(self, user=None, request=None, requestid=None,
                      logger=None, **kwargs):
        raising_exception = None
        rollback_failed = False
        dbuser = None
        session = None
        exporter = None

        if not self.requires_readonly \
           and self.config.get('broker', 'mode') != 'readwrite':
            # pragma: no cover
            raise UnimplementedError("Command %s not available on a "
                                     "read-only broker." % self.command)

        try:
            if self.requires_transaction:
                # Set up a session...
                if self.is_lock_free:
                    session = self.dbf.NLSession()
                else:
                    session = self.dbf.Session()

                # Create an exporter to handle external events.  We stash this
                # in the session.info dict to provide access to other users.
                # (note that session.info is designed for this purpose)
                # Listen to flush events and use them to tell the exporter
                # when various objects have chnaged.
                exporter = Exporter(logger=logger, requestid=requestid, user=user)
                event.listen(session, "after_flush", exporter.event_after_flush)
                session.info['exporter'] = exporter

                # Force connecting to the DB
                try:
                    conn = session.connection()
                except DatabaseError as err:  # pragma: no cover
                    raise TransientError("Failed to connect to the "
                                         "database: %s" % err)

                if session.bind.dialect.name == "oracle":
                    # Make the name of the command and the request ID
                    # available in v$session. Trying to set a value longer
                    # than the allowed length will generate ORA-24960, so
                    # do an explicit truncation.
                    dbapi_con = conn.connection.connection
                    dbapi_con.action = str(self.action)[:32]
                    # TODO: we should include the command number as well,
                    # since that is easier to find in the logs
                    dbapi_con.clientinfo = str(requestid)[:64]

                # This does a COMMIT, which in turn invalidates the session.
                # We should therefore avoid looking up anything in the DB
                # before this point which might be used later.
                status = request.status
                start_xtn(session, status.requestid, status.user,
                          status.command, self.requires_readonly,
                          kwargs, _IGNORED_AUDIT_ARGS)

                dbuser = get_or_create_user_principal(session, user,
                                                      commitoncreate=True,
                                                      logger=logger)

                self.az.check(principal=user, dbuser=dbuser,
                              action=self.action, resource=request.path)

                if self.requires_readonly:
                    self._set_readonly(session)
                # begin() is only required if session transactional=False
                # session.begin()

            if self.requires_plenaries:
                plenaries = PlenaryCollection(logger=logger)
            else:
                plenaries = None

            retval = self.render(user=user, dbuser=dbuser, request=request,
                                 requestid=requestid, logger=logger,
                                 plenaries=plenaries,
                                 session=session, **kwargs)
            if self.requires_format:
                style = kwargs.get("style", None)
                retval = self.formatter.format(style, retval, request)
            if session:
                with exporter:
                    session.commit()
            return retval
        except Exception as e:
            raising_exception = e
            # Need to close after the rollback, or the next time session
            # is accessed it tries to commit the transaction... (?)
            if session:
                try:
                    session.rollback()
                except:  # pragma: no cover
                    rollback_failed = True
                    raise
                session.close()
            if logger:
                # Knowing which exception class was thrown might be useful
                logger.info("%s: %s", type(e).__name__, e)
            raise
        finally:
            # Obliterating the scoped_session - next call to session()
            # will create a new one.
            if session:
                # Complete the transaction. We really want to get rid of the
                # session, even if end_xtn() fails
                try:
                    if not rollback_failed:
                        # If session.rollback() failed for whatever reason,
                        # our best bet is to avoid touching the session
                        end_xtn(session, requestid,
                                get_code_for_error_class(
                                    raising_exception.__class__),
                                getattr(request, '_audit_result', None))
                finally:
                    if self.is_lock_free:
                        self.dbf.NLSession.remove()
                    else:
                        self.dbf.Session.remove()
            if logger:
                self._cleanup_logger(logger)

    def _set_readonly(self, session):
        if session.bind.dialect.name == "oracle" or \
           session.bind.dialect.name == "postgresql":
            session.commit()
            session.execute(text("set transaction read only"))

    # This is meant to be called before calling invoke_render() in order to
    # add a logger into the argument list.  It returns the arguments
    # that will be passed into invoke_render().
    def add_logger(self, request, **command_kwargs):
        if self.command != "show_request":
            # For the show_request requestid is the UUID of the comamnd we
            # want intofmation for and not the UUID of this command.  As
            # a result show_request commands do not have a requestid.
            requestid = command_kwargs.get("requestid", None)
            command_kwargs['requestid'] = \
                self.catalog.store_requestid(request.status, requestid)
        user = request.getPrincipal()
        request.status.create_description(user=user, command=self.command,
                                          kwargs=command_kwargs,
                                          ignored=_IGNORED_AUDIT_ARGS)
        logger = RequestLogger(status=request.status, module_logger=self.module_logger)
        kwargs_str = str(request.status.args)
        if len(kwargs_str) > 1024:
            kwargs_str = kwargs_str[0:1020] + '...'
        logger.info("Incoming command #%s from user=%s aq %s "
                    "with arguments %s",
                    request.status.auditid, request.status.user,
                    request.status.command, kwargs_str)
        command_kwargs["logger"] = logger
        command_kwargs["user"] = user
        command_kwargs["request"] = request
        return command_kwargs

    def _cleanup_logger(self, logger):
        logger.debug("Server finishing request.")
        logger.close_handlers()

    @property
    def is_lock_free(self):
        if self._is_lock_free is None:
            self._is_lock_free = self.is_class_lock_free()
        return self._is_lock_free

    # A set of heuristics is provided as a default that works well
    # enough for most commands to set the _is_lock_free flag used
    # above.
    #
    # If the module has a Plenary class or a LockKey class imported it
    # is a good indication that a lock will be taken.
    #
    # This can be overridden per-command if general heuristics are not
    # enough.  This algorithm accounts for aliased (subclassed)
    # commands like reconfigure by calling this method on the superclass.
    # There is also an override in __init__ for the cat commands since
    # they all use Plenary classes but do not require a lock.
    @classmethod
    def is_class_lock_free(cls):
        if cls.requires_plenaries:
            return False

        for item in sys.modules[cls.__module__].__dict__.values():
            # log.msg("  Checking %s" % item)
            if item in [sync_domain, TemplateDomain]:
                return False
            if not isclass(item):
                continue
            if issubclass(item, Plenary) or issubclass(item, Chooser) or \
               issubclass(item, LockKey) or \
               issubclass(item, PlenaryCollection):
                return False
            if item != cls and item != BrokerCommand and \
               issubclass(item, BrokerCommand):
                if item.__module__ not in sys.modules:  # pragma: no cover
                    log.msg("Cannot evaluate %s, too early." % cls)
                    return False
                if item._is_lock_free is not None:
                    super_is_free = item._is_lock_free
                else:
                    super_is_free = item.is_class_lock_free()
                # log.msg("%s says %s" % (item, super_is_free))
                # If the superclass needs a lock, we need a lock.
                # However, if the superclass does not need a lock, keep
                # checking in case the subclass imports something else
                # that requires a lock.
                if not super_is_free:
                    return super_is_free
        return True

    @classmethod
    def deprecated_command(cls, msg, logger=None, user=None, **_):
        if not logger:  # pragma: no cover
            raise AquilonError("Too few arguments to deprecated_command")

        # cls.__name__ is good enough to mine the logs which deprecated commands
        # are still in use.

        if not user:
            user = "anonymous"

        logger.info("User %s invoked deprecated command %s" % (user,
                                                               cls.__name__))
        logger.client_info(msg)

    @classmethod
    def deprecated_option(cls, option, msg="", logger=None, user=None, **_):
        if not option or not logger:  # pragma: no cover
            raise AquilonError("Too few arguments to deprecated_option")

        if not user:
            user = "anonymous"

        # cls.__name__ is good enough to mine the logs which deprecated options
        # are still in use.
        logger.info("User %s used deprecated option %s of command %s" %
                    (user, option, cls.__name__))
        logger.client_info("The --%s option is deprecated.  %s" % (option, msg))

    @classmethod
    def require_one_of(cls, *args, **kwargs):
        if args:
            # Take 'args' as the list of keys that we are going to check
            # exist in 'kwargs', we will ignore any addition 'kwargs'
            count = sum(1 if kwargs.get(arg, None) else 0 for arg in args)
        else:
            # Make sure only one of the supplied arguments is set
            count = sum(1 if x else 0 for x in kwargs.values())
        if count != 1:
            if args:
                names = ["--%s" % arg for arg in args]
            else:
                names = ["--%s" % arg for arg in kwargs]
            raise ArgumentError("Exactly one of %s should be sepcified." %
                                (', '.join(names[:-1]) + ' and ' + names[-1]))
