# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2016  Contributor
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
"""Contains the logic for `aq search observed mac`."""

from aquilon.aqdb.model import ObservedMac, NetworkDevice
from aquilon.worker.broker import BrokerCommand


class CommandSearchObservedMac(BrokerCommand):

    required_parameters = []
    default_style = "csv"

    def render(self, session, logger, network_device, switch, port, mac,
               **arguments):
        if switch:
            self.deprecated_option("switch", "Please use --network_device "
                                   "instead.", logger=logger, **arguments)
            if not network_device:
                network_device = switch
        q = session.query(ObservedMac)
        if network_device:
            dbnetdev = NetworkDevice.get_unique(session, network_device, compel=True)
            q = q.filter_by(network_device=dbnetdev)
        if port is not None:
            q = q.filter_by(port=port)
        if mac:
            q = q.filter_by(mac_address=mac)
        return q.order_by(ObservedMac.mac_address).all()
