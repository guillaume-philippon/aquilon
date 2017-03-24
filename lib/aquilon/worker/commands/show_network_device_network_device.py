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
"""Contains the logic for `aq show network_device --network_device`."""

from sqlalchemy.orm import joinedload, subqueryload, undefer

from aquilon.aqdb.model import NetworkDevice
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.network_device import discover_network_device
from aquilon.worker.formats.list import StringList


class CommandShowNetworkDevice(BrokerCommand):

    required_parameters = ["network_device"]

    def render(self, session, logger, network_device, discover, **_):
        if discover:
            options = []
        else:
            options = [undefer('comments'),
                       joinedload('host'),
                       undefer('host.comments'),
                       undefer('host.personality_stage.personality.archetype.comments'),
                       subqueryload('port_groups'),
                       undefer('port_groups.creation_date'),
                       joinedload('port_groups.network'),
                       subqueryload('observed_macs'),
                       undefer('observed_macs.creation_date')]
        dbnetdev = NetworkDevice.get_unique(session, network_device, compel=True,
                                            query_options=options)
        if discover:
            results = discover_network_device(session, logger, self.config,
                                              dbnetdev, True)
            return StringList(results)
        else:
            return dbnetdev
