# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2014,2016  Contributor
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
"""Contains the logic for `aq poll network_device --network_device`."""


from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.poll_network_device import CommandPollNetworkDevice
from aquilon.aqdb.model import NetworkDevice


class CommandPollNetworkDeviceNetworkDevice(CommandPollNetworkDevice):

    required_parameters = ["network_device"]

    def render(self, session, logger, network_device, type, clear, vlan, **_):
        NetworkDevice.check_type(type)
        dbnetdev = NetworkDevice.get_unique(session, network_device, compel=True)
        if type is not None and dbnetdev.switch_type != type:
            raise ArgumentError("{0} is not a {1} switch.".format(dbnetdev,
                                                                  type))
        return self.poll(session, logger, [dbnetdev], clear, vlan)
