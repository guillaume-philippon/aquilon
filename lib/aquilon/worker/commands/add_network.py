# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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

import math
from ipaddr import IPv4Network, AddressValueError, NetmaskValueError

from aquilon.exceptions_ import ArgumentError, NotFoundException
from aquilon.aqdb.model import Network, NetworkEnvironment, NetworkCompartment
from aquilon.aqdb.model.network import get_net_id_from_ip
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.location import get_location


class CommandAddNetwork(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["network", "ip"]

    def render(self, session, logger, plenaries, dbuser,
               network, ip, network_environment, type, side, comments,
               netmask, prefixlen, mask, network_compartment, **arguments):

        # Handle the different ways of specifying the netmask
        self.require_one_of(netmask=netmask, prefixlen=prefixlen, mask=mask)
        if prefixlen:
            netmask = prefixlen
        elif mask:
            netmask = 32 - int(math.log(mask, 2))

        try:
            address = IPv4Network("%s/%s" % (ip, netmask))
        except AddressValueError as e:
            raise ArgumentError("Failed to parse the network address: %s" % e)
        except NetmaskValueError as e:
            raise ArgumentError("Failed to parse the netmask: %s" % e)

        if ip != address.network:
            raise ArgumentError("IP address %s is not a network address.  "
                                "Maybe you meant %s?" % (ip, address.network))

        location = get_location(session, **arguments)
        if not type:
            type = 'unknown'
        if not side:
            side = 'a'

        dbnet_env = NetworkEnvironment.get_unique_or_default(session,
                                                             network_environment)
        self.az.check_network_environment(dbuser, dbnet_env)

        if network_compartment:
            dbcomp = NetworkCompartment.get_unique(session,
                                                   network_compartment,
                                                   compel=True)
        else:
            dbcomp = None

        # Check if the name is free. Network names are not unique in QIP and
        # there is no uniqueness constraint in AQDB, so only warn if the name is
        # already in use.
        q = session.query(Network).filter_by(name=network)
        dbnetwork = q.first()
        if dbnetwork:
            logger.client_info("WARNING: Network name %s is already used for "
                               "address %s." % (network, str(dbnetwork.network)))

        # Check if the address is free
        try:
            dbnetwork = get_net_id_from_ip(session, address.ip,
                                           network_environment=dbnet_env)
            raise ArgumentError("IP address %s is part of existing network "
                                "named %s with address %s." %
                                (str(address.ip), dbnetwork.name,
                                 str(dbnetwork.network)))
        except NotFoundException:
            pass

        # Okay, all looks good, let's create the network
        net = Network(name=network, network=address,
                      network_environment=dbnet_env, network_type=type,
                      side=side, location=location, comments=comments,
                      network_compartment=dbcomp)

        session.add(net)
        session.flush()

        plenaries.add(net)
        plenaries.write()

        return
