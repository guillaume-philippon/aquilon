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
"""Contains the logic for `aq del interface`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Interface
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.hardware_entity import get_hardware


class CommandDelInterface(BrokerCommand):
    requires_plenaries = True

    required_parameters = []

    def render(self, session, logger, plenaries, interface, switch, mac, user,
               **arguments):
        if switch:
            self.deprecated_option("switch", "Please use --network_device "
                                   "instead.", logger=logger, user=user,
                                   **arguments)
            arguments["network_device"] = switch

        dbhw_ent = get_hardware(session, compel=False, **arguments)
        dbinterface = Interface.get_unique(session, hardware_entity=dbhw_ent,
                                           name=interface, mac=mac, compel=True)
        if not dbhw_ent:
            dbhw_ent = dbinterface.hardware_entity

        if dbinterface.vlans:
            vlans = ", ".join(sorted(iface.name for iface in
                                     dbinterface.vlans.values()))
            raise ArgumentError("{0} is the parent of the following VLAN "
                                "interfaces, delete them first: "
                                "{1}.".format(dbinterface, vlans))

        if dbinterface.slaves:
            slaves = ", ".join(sorted(iface.name for iface in
                                      dbinterface.slaves))
            raise ArgumentError("{0} is the master of the following slave "
                                "interfaces, delete them first: "
                                "{1}.".format(dbinterface, slaves))

        if dbinterface.service_addresses:
            srvs = ", ".join(sorted(srv.name for srv in
                                    dbinterface.service_addresses))
            raise ArgumentError("{0} still has the following service "
                                "addresses bound to it, delete them first: "
                                "{1}.".format(dbinterface, srvs))

        for addr in dbinterface.assignments:
            if addr.ip != dbhw_ent.primary_ip:
                continue

            # If this is a machine, it is possible to delete the host to get rid
            # of the primary name
            if dbhw_ent.hardware_type == "machine":
                msg = "  You should delete the host first."
            else:
                msg = ""

            raise ArgumentError("{0} holds the primary address of the {1:cl}, "
                                "therefore it cannot be deleted."
                                "{2}".format(dbinterface, dbhw_ent, msg))

        addrs = ", ".join(sorted("%s: %s" % (addr.logical_name, addr.ip)
                                 for addr in dbinterface.assignments))
        if addrs:
            raise ArgumentError("{0} still has the following addresses "
                                "configured, delete them first: "
                                "{1}.".format(dbinterface, addrs))

        dbhw_ent.interfaces.remove(dbinterface)
        session.flush()

        if dbhw_ent.hardware_type != 'chassis':
            plenaries.add(dbhw_ent)
            if dbhw_ent.host:
                plenaries.add(dbhw_ent.host)
            plenaries.write()
        return
