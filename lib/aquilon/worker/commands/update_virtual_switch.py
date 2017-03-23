# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2012,2014,2016  Contributor
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
"""Contains the logic for `aq update virtual switch`."""

from aquilon.aqdb.model import VirtualSwitch
from aquilon.worker.broker import BrokerCommand


class CommandUpdateVirtualSwitch(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["virtual_switch"]

    def render(self, session, plenaries, virtual_switch, comments, **_):
        dbvswitch = VirtualSwitch.get_unique(session, virtual_switch,
                                             compel=True)

        if comments is not None:
            dbvswitch.comments = comments

        session.flush()

        plenaries.add(dbvswitch)
        plenaries.write()
