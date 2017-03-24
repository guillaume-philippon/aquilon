# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017  Contributor
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
"""Contains the logic for `aq add network_device`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import NetworkDevice, Model, Archetype
from aquilon.aqdb.model.network import get_net_id_from_ip
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.dns import grab_address
from aquilon.worker.dbwrappers.location import get_location
from aquilon.worker.dbwrappers.interface import (get_or_create_interface,
                                                 assign_address,
                                                 check_netdev_iftype)
from aquilon.worker.dbwrappers.host import create_host
from aquilon.worker.processes import DSDBRunner
from aquilon.worker.templates.switchdata import PlenarySwitchData


class CommandAddNetworkDevice(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["network_device", "model", "type",
                           "ip", "interface", "iftype"]

    def render(self, session, logger, plenaries, network_device, label, model, type, ip,
               interface, iftype, mac, vendor, serial, comments,
               archetype, domain, sandbox, **arguments):
        dbmodel = Model.get_unique(session, name=model, vendor=vendor,
                                   compel=True)

        if not dbmodel.model_type.isNetworkDeviceType():
            raise ArgumentError("This command can only be used to "
                                "add network devices.")

        dblocation = get_location(session, compel=True, **arguments)

        dbdns_rec, _ = grab_address(session, network_device, ip,
                                    allow_restricted_domain=True,
                                    allow_reserved=True, preclude=True)
        if not label:
            label = dbdns_rec.fqdn.name
            try:
                NetworkDevice.check_label(label)
            except ArgumentError:
                raise ArgumentError("Could not deduce a valid hardware label "
                                    "from the network device name.  Please specify "
                                    "--label.")

        # FIXME: What do the error messages for an invalid enum (switch_type)
        # look like?
        dbnetdev = NetworkDevice(label=label, switch_type=type,
                                 location=dblocation, model=dbmodel,
                                 serial_no=serial, comments=comments)
        session.add(dbnetdev)
        dbnetdev.primary_name = dbdns_rec

        check_netdev_iftype(iftype)

        dbinterface = get_or_create_interface(session, dbnetdev,
                                              name=interface, mac=mac,
                                              interface_type=iftype)
        dbnetwork = get_net_id_from_ip(session, ip)
        # TODO: should we call check_ip_restrictions() here?
        assign_address(dbinterface, ip, dbnetwork, logger=logger)

        if not archetype:
            hw_section = 'hardware_network_device'
            if not self.config.has_option(hw_section, 'default_archetype'):
                raise ArgumentError("Cannot determine the archetype for "
                                    "network devices.  Please specify "
                                    "--archetype.")
            archetype = self.config.get(hw_section, 'default_archetype')

        dbarchetype = Archetype.get_unique(session, archetype, compel=True)

        dbhost = create_host(session, logger, self.config, dbnetdev,
                             dbarchetype, domain=domain, sandbox=sandbox,
                             **arguments)

        session.flush()

        # Add the legacy template separately
        plenaries.add(dbnetdev, cls=PlenarySwitchData)
        plenaries.add(dbnetdev)
        plenaries.add(dbhost)

        with plenaries.transaction():
            dsdb_runner = DSDBRunner(logger=logger)
            dsdb_runner.update_host(dbnetdev, None)
            dsdb_runner.commit_or_rollback("Could not add network device to DSDB")

        return
