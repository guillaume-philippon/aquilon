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
"""Contains the logic for `aq add manager`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.host import hostname_to_host
from aquilon.worker.dbwrappers.dns import grab_address
from aquilon.worker.dbwrappers.interface import (generate_ip,
                                                 get_or_create_interface,
                                                 assign_address)
from aquilon.worker.processes import DSDBRunner


class CommandAddManager(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["hostname"]

    def render(self, session, logger, plenaries, hostname, manager, interface, mac,
               comments, **arguments):
        dbhost = hostname_to_host(session, hostname)
        dbmachine = dbhost.hardware_entity
        oldinfo = DSDBRunner.snapshot_hw(dbmachine)
        audit_results = []

        if not manager:
            manager = "%sr.%s" % (dbmachine.primary_name.fqdn.name,
                                  dbmachine.primary_name.fqdn.dns_domain.name)
            logger.info("Selected manager {0!s} for {1:l}."
                        .format(manager, dbhost))
            audit_results.append(('manager', manager))

        dbinterface = get_or_create_interface(session, dbmachine,
                                              name=interface, mac=mac,
                                              interface_type='management')

        addrs = ", ".join(sorted("%s [%s]" % (addr.logical_name, addr.ip)
                                 for addr in dbinterface.assignments))
        if addrs:
            raise ArgumentError("{0} already has the following addresses: "
                                "{1}.".format(dbinterface, addrs))

        ip = generate_ip(session, logger, dbinterface, compel=True,
                         audit_results=audit_results, **arguments)

        dbdns_rec, _ = grab_address(session, manager, ip, comments=comments,
                                    preclude=True)

        assign_address(dbinterface, ip, dbdns_rec.network, logger=logger)

        session.flush()

        plenaries.add(dbmachine)
        with plenaries.transaction():
            dsdb_runner = DSDBRunner(logger=logger)
            dsdb_runner.update_host(dbmachine, oldinfo)
            dsdb_runner.commit_or_rollback("Could not add host to DSDB")

        if dbmachine.host:
            # XXX: Host needs to be reconfigured.
            pass

        for name, value in audit_results:
            self.audit_result(session, name, value, **arguments)
        return
