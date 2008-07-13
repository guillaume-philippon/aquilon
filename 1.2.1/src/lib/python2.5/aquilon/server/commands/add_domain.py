#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq add domain`."""


import os

from aquilon.exceptions_ import AuthorizationException
from aquilon.server.broker import (format_results, add_transaction, az_check,
                                   BrokerCommand)
from aquilon.aqdb.sy.domain import Domain
from aquilon.server.dbwrappers.user_principal import (
        get_or_create_user_principal)
from aquilon.server.dbwrappers.quattor_server import (
        get_or_create_quattor_server)
from aquilon.server.processes import run_command


class CommandAddDomain(BrokerCommand):

    required_parameters = ["domain"]

    @add_transaction
    @az_check
    def render(self, session, domain, user, **arguments):
        dbuser = get_or_create_user_principal(session, user)
        if not dbuser:
            raise AuthorizationException("Cannot create a domain without"
                    + " an authenticated connection.")
        dbquattor_server = get_or_create_quattor_server(session,
                self.config.get("broker", "servername"))
        # For now, succeed without error if the domain already exists.
        dbdomain = session.query(Domain).filter_by(name=domain).first()
        # FIXME: Check that the domain name is composed only of characters
        # that are valid for a directory name.
        if not dbdomain:
            dbdomain = Domain(domain, dbquattor_server, dbuser)
            session.save_or_update(dbdomain)
        domaindir = os.path.join(self.config.get("broker", "templatesdir"),
                dbdomain.name)
        # FIXME: If this command fails, should the domain entry be
        # created in the database anyway?
        git_env={"PATH":"%s:%s" % (self.config.get("broker", "git_path"),
            os.environ.get("PATH", ""))}
        run_command(["git", "clone", self.config.get("broker", "kingdir"),
            domaindir], env=git_env)
        # The 1.0 code notes that this should probably be done as a
        # hook in git... just need to make sure it runs.
        run_command(["git-update-server-info"], env=git_env, path=domaindir)
        return


#if __name__=='__main__':
