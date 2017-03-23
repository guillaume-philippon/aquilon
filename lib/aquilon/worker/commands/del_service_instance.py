# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2015,2016  Contributor
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
"""Contains a wrapper for `aq del service --instance`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Service, ServiceInstance
from aquilon.worker.broker import BrokerCommand


class CommandDelServiceInstance(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["service", "instance"]

    def render(self, session, plenaries, service, instance, **_):
        dbservice = Service.get_unique(session, service, compel=True)
        dbsi = ServiceInstance.get_unique(session, service=dbservice,
                                          name=instance, compel=True)
        if dbsi.client_count:
            raise ArgumentError("Service %s, instance %s still has clients and "
                                "cannot be deleted." %
                                (dbservice.name, dbsi.name))
        if dbsi.servers:
            msg = ", ".join(sorted(srv.fqdn for srv in dbsi.servers))
            raise ArgumentError("Service %s, instance %s is still being "
                                "provided by servers: %s." %
                                (dbservice.name, dbsi.name, msg))

        plenaries.add(dbsi)

        # Depend on cascading to remove any mappings
        session.delete(dbsi)
        session.flush()

        plenaries.write()

        return
