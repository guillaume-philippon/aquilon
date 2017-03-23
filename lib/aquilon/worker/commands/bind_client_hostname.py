# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2014,2015,2016  Contributor
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
"""Contains the logic for `aq bind client --hostname`."""

from aquilon.aqdb.model import Service, ServiceInstance
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.host import hostname_to_host
from aquilon.worker.services import Chooser


class CommandBindClientHostname(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["hostname", "service"]

    def render(self, session, logger, plenaries, hostname, service, instance, force=False,
               **_):
        dbhost = hostname_to_host(session, hostname)
        dbservice = Service.get_unique(session, service, compel=True)
        chooser = Chooser(dbhost, plenaries, logger=logger, required_only=False)
        if instance:
            dbinstance = ServiceInstance.get_unique(session, service=dbservice,
                                                    name=instance, compel=True)
            chooser.set_single(dbservice, dbinstance, force=force)
        else:
            chooser.set_single(dbservice, force=force)

        session.flush()

        plenaries.write()

        return
