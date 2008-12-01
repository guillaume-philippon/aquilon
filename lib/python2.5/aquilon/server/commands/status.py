# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq status`."""


from aquilon.server.broker import BrokerCommand
from aquilon.server.dbwrappers.user_principal import (
        get_or_create_user_principal)


class CommandStatus(BrokerCommand):

    requires_format = True

    def render(self, session, user, **arguments):
        stat = []
        stat.append("Aquilon Broker %s" % self.config.get("broker", "version"))
        stat.append("Server: %s" % self.config.get("broker", "servername"))
        stat.append("Database: %s" % self.config.get("database", "dsn"))
        dbuser = get_or_create_user_principal(session, user)
        if dbuser:
            stat.append("Connected as: %s [%s]" % (dbuser, dbuser.role.name))
        return stat


