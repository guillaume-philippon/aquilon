# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2013,2014,2015,2016  Contributor
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

from aquilon.aqdb.model import (OperatingSystem, Archetype,
                                AssetLifecycle)
from aquilon.worker.broker import BrokerCommand
from aquilon.utils import validate_template_name, validate_nlist_key


class CommandAddOS(BrokerCommand):

    required_parameters = ["osname", "osversion", "archetype"]

    def render(self, session, osname, osversion, archetype, copy_version,
               comments, **_):
        validate_nlist_key("--osname", osname)
        validate_template_name("--osversion", osversion)

        dbarchetype = Archetype.get_unique(session, archetype, compel=True)
        OperatingSystem.get_unique(session, name=osname, version=osversion,
                                   archetype=dbarchetype, preclude=True)

        if copy_version:
            dbprev_os = OperatingSystem.get_unique(session, name=osname,
                                                   version=copy_version,
                                                   archetype=dbarchetype,
                                                   compel=True)

            if comments is None:
                comments = dbprev_os.comments

        dblifecycle = AssetLifecycle.get_instance(session, "evaluation")

        dbos = OperatingSystem(name=osname, version=osversion,
                               archetype=dbarchetype,
                               lifecycle=dblifecycle,
                               comments=comments)
        session.add(dbos)

        if copy_version:
            dbos.required_services.extend(dbprev_os.required_services)

        session.flush()
        return
