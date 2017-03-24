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
"""Contains the logic for `aq del service`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Service
from aquilon.worker.broker import BrokerCommand


class CommandDelService(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["service"]

    def render(self, session, plenaries, service, **_):
        dbservice = Service.get_unique(session, service, compel=True)

        if dbservice.archetypes:
            msg = ", ".join(sorted(archetype.name
                                   for archetype in dbservice.archetypes))
            raise ArgumentError("Service %s is still required by the following "
                                "archetypes: %s." % (dbservice.name, msg))
        if dbservice.personality_assignments:
            msg = ", ".join(sorted(link.personality_stage.qualified_name
                                   for link in dbservice.personality_assignments))
            raise ArgumentError("Service %s is still required by the following "
                                "personalities: %s." % (dbservice.name, msg))
        if dbservice.instances:
            raise ArgumentError("Service %s still has instances defined and "
                                "cannot be deleted." % dbservice.name)

        plenaries.add(dbservice)

        session.delete(dbservice)
        session.flush()

        plenaries.write()

        return
