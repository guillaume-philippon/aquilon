# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013,2014,2015,2016  Contributor
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
""" Xtn (transaction) is an audit trail of all broker activity """
import logging
from datetime import datetime
from dateutil.tz import tzutc
from six.moves.urllib_parse import quote  # pylint: disable=F0401
from six import iteritems

from sqlalchemy import (Column, String, Integer, Boolean, ForeignKey,
                        PrimaryKeyConstraint, Index)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import desc

from aquilon.config import Config
from aquilon.aqdb.model.base import Base
from aquilon.aqdb.column_types import GUID, UTCDateTime

config = Config()
log = logging.getLogger('aquilon.aqdb.model.xtn')


def utcnow(context, tz=tzutc()):  # pylint: disable=W0613
    return datetime.now(tz)


class Xtn(Base):
    """ auditing information from command invocations """
    __tablename__ = 'xtn'

    id = Column(GUID, primary_key=True)
    username = Column(String(65), nullable=False, default='nobody')
    command = Column(String(64), nullable=False)
    # This column is *massively* redundant, but we're fully denormalized
    is_readonly = Column(Boolean, nullable=False)
    # Force the use of UTC if the underlying data type does not handle time zone
    # information correctly
    start_time = Column(UTCDateTime(timezone=True),
                        default=utcnow, nullable=False)

    end = relationship("XtnEnd", uselist=False, lazy="joined")
    # N.B. NO "cascade". Transaction logs are *never* deleted/changed
    # Given that, we don't really *need* the foreign key, but we'll keep it
    # unless it proves otherwise cumbersome for performance (mainly insert).

    __table_args__ = (Index('xtn_username_idx', username, oracle_bitmap=True),
                      Index('xtn_command_idx', command, oracle_bitmap=True),
                      Index('xtn_is_readonly_idx', is_readonly,
                            oracle_bitmap=True),
                      Index('xtn_start_time_idx', desc(start_time)),
                      {'oracle_compress': 'OLTP'})

    @property
    def return_code(self):
        """ List the return code as 0 for commands that are not completed."""
        if self.end:
            return self.end.return_code
        else:
            return 0

    def __str__(self):
        if self.end:
            return_code = self.end.return_code
        else:
            return_code = '-'

        msg = [self.start_time.strftime('%Y-%m-%d %H:%M:%S%z'),
               str(self.username), str(return_code), 'aq', str(self.command)]
        results = []
        for arg in self.args:
            if arg.name == "__RESULT__":  # pragma: no cover
                # We no longer generate this form, but it exists in the DB
                results.append(arg.value)
                continue
            elif arg.name.startswith("__RESULT__:"):
                results.append("%s=%s" % (arg.name[11:], arg.value))
                continue

            # TODO: remove the str() once we can handle Unicode
            try:
                msg.append("--%s=%r" % (arg.name, str(arg.value)))
            except UnicodeEncodeError:  # pragma: no cover
                msg.append("--%s=<Non-ASCII value>" % arg.name)
        if results:
            msg.append("[Result: " + " ".join(results) + "]")
        return " ".join(msg)


class XtnEnd(Base):
    """ A record of a completed command/transaction """
    __tablename__ = 'xtn_end'
    xtn_id = Column(ForeignKey(Xtn.id), primary_key=True)
    return_code = Column(Integer, nullable=False)
    end_time = Column(UTCDateTime(timezone=True),
                      default=utcnow, nullable=False)

    __table_args__ = (Index('xtn_end_return_code_idx', return_code,
                            oracle_bitmap=True),
                      {'oracle_compress': 'OLTP'})


class XtnDetail(Base):
    """ Key/Value argument pairs for executed commands """
    __tablename__ = 'xtn_detail'

    xtn_id = Column(ForeignKey(Xtn.id), nullable=False)
    name = Column(String(255), nullable=False)
    # Note: Oracle has limits on the maximum size of all columns in an index, so
    # we cannot make this column too large.
    value = Column(String(3000), nullable=False)

    __table_args__ = (PrimaryKeyConstraint(xtn_id, name, value),
                      Index('xtn_detail_name_idx', name, oracle_bitmap=True),
                      Index('xtn_detail_value_idx', value, oracle_bitmap=True),
                      {'oracle_compress': 'OLTP'})

Xtn.args = relationship(XtnDetail, lazy="joined", order_by=[XtnDetail.name])


if config.has_option('database', 'audit_schema'):  # pragma: no cover
    schema = config.get('database', 'audit_schema')
    Xtn.__table__.schema = schema
    XtnEnd.__table__.schema = schema
    XtnDetail.__table__.schema = schema


def start_xtn(session, xtn_id, username, command, is_readonly, details, ignore):
    """ Wrapper to log the start of a transaction (or running command).

    Takes a dictionary with the transaction parameters.  The keys are
    command, usename, readonly, and details.  The details parameter
    is itself a a dictionary of option names to option values provided
    for the command.

    The options_to_split is a list of any options that need to be
    split on newlines.  Typically this is --list and/or --hostlist.

    """
    # TODO: one day we should be able to handle non-ASCII characters..
    def sanitized_string(value):
        try:
            return str(value).decode('ascii')
        except UnicodeDecodeError:
            return quote(value)

    # TODO: (maybe) use sql inserts instead of objects to avoid added overhead?
    # We would be able to exploit executemany() for all the xtn_detail rows
    x = Xtn(id=xtn_id, command=command, username=username,
            is_readonly=is_readonly)
    session.add(x)

    for key, value in iteritems(details):
        if key in ignore:
            continue

        # Ignore optional parameters that were not specified
        if value is None:
            continue

        # The --format command-line option is tricky, as the client does not
        # pass it as a query parameter, but as a file extension. For historic
        # reasons, the broker converts that information to an option named
        # 'style'; convert it back to be compatible with the old reporting
        # format.
        if key == 'style':
            key = 'format'

        # Skip uber-redundant raw format parameter
        if key == 'format' and value == 'raw':
            continue

        # Sometimes we delete a value and the arg comes in as an empty
        # string.  Denote this with a dash '-' to work around Oracle
        # not being able to store the concept of a non-NULL empty string.
        if value == '':
            value = '-'

        if isinstance(value, list):
            for item in value:
                session.add(XtnDetail(xtn_id=xtn_id, name=key,
                                      value=sanitized_string(item)))
        else:
            session.add(XtnDetail(xtn_id=xtn_id, name=key,
                                  value=sanitized_string(value)))

    try:
        session.commit()
    except Exception as e:  # pragma: no cover
        session.rollback()
        log.error(e)
        # Abort the command if a log entry cannot be created.
        raise


def end_xtn(session, xtn_id, return_code, results=None):
    """ Take an audit message and commit the transaction completion. """

    session.add(XtnEnd(xtn_id=xtn_id, return_code=return_code))
    if results:
        for name, value in results:
            session.add(XtnDetail(xtn_id=xtn_id, name='__RESULT__:' + str(name),
                                  value=str(value)))

    try:
        session.commit()
    except Exception as e:  # pragma: no cover
        session.rollback()
        log.error(e)
        # Swallow the error - can't do anything about this, and the
        # user really can't do anything about this.
