# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014  Contributor
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
"""Contains the logic for `aq add interface address --network_device`."""

from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.add_interface_address import CommandAddInterfaceAddress


class CommandAddInterfaceAddressNetworkDevice(CommandAddInterfaceAddress):

    required_parameters = ['network_device', 'interface']

    def render(self, map_to_primary, **kwargs):

        # Reverse PTR control. For network devices we should default to
        # having the forward and reverse DNS names the same.
        if map_to_primary is None:
            map_to_primary = False
        kwargs['map_to_primary'] = map_to_primary

        return CommandAddInterfaceAddress.render(self, **kwargs)
