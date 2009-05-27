# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq show machine --all`."""


from aquilon.server.broker import BrokerCommand
from aquilon.server.formats.machine import SimpleMachineList
from aquilon.aqdb.model import Machine


class CommandShowHostAll(BrokerCommand):

    def render(self, session, **arguments):
        return SimpleMachineList(session.query(Machine).all())


