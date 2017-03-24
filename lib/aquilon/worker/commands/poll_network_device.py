# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017  Contributor
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
"""Contains the logic for `aq poll network_device`."""

from csv import DictReader, Error as CSVError
from json import JSONDecoder
from datetime import datetime

from six.moves import cStringIO as StringIO  # pylint: disable=F0401

from aquilon.exceptions_ import (AquilonError, ArgumentError, NotFoundException,
                                 ProcessException)
from aquilon.utils import force_ipv4, validate_json
from aquilon.aqdb.types import MACAddress
from aquilon.aqdb.model import (NetworkDevice, ObservedMac, PortGroup, Network,
                                NetworkEnvironment, VlanInfo, Rack)
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.observed_mac import (
    update_or_create_observed_mac)
from aquilon.worker.dbwrappers.network_device import (determine_helper_hostname,
                                                      determine_helper_args)
from aquilon.worker.locks import ExternalKey
from aquilon.worker.processes import run_command


class CommandPollNetworkDevice(BrokerCommand):

    required_parameters = ["rack"]

    def render(self, session, logger, rack, type, clear, vlan, **_):
        dblocation = Rack.get_unique(session, rack, compel=True)
        NetworkDevice.check_type(type)
        q = session.query(NetworkDevice)
        q = q.filter_by(location=dblocation)
        if type:
            q = q.filter_by(switch_type=type)
        netdevs = q.all()
        if not netdevs:
            raise NotFoundException("No network device found.")
        return self.poll(session, logger, netdevs, clear, vlan)

    def poll(self, session, logger, netdevs, clear, vlan):
        now = datetime.now()
        failed_vlan = 0
        default_ssh_args = determine_helper_args(self.config)
        for netdev in netdevs:
            if clear:
                self.clear(session, netdev)

            hostname = determine_helper_hostname(session, logger, self.config,
                                                 netdev)
            if hostname:
                ssh_args = default_ssh_args[:]
                ssh_args.append(hostname)
            else:
                ssh_args = []

            with ExternalKey("poll_network_device", [netdev], logger=logger):
                self.poll_mac(session, netdev, now, ssh_args)
                if vlan:
                    if netdev.switch_type != "tor":
                        logger.client_info("Skipping VLAN probing on {0:l}, it's "
                                           "not a ToR network device.".format(netdev))
                        continue

                    try:
                        self.poll_vlan(session, logger, netdev, now, ssh_args)
                    except ProcessException as e:
                        failed_vlan += 1
                        logger.client_info("Failed getting VLAN info for {0:l}: "
                                           "{1!s}".format(netdev, e))
        if netdevs and failed_vlan == len(netdevs):
            raise ArgumentError("Failed getting VLAN info.")
        return

    def poll_mac(self, session, netdev, now, ssh_args):
        importer = self.config.lookup_tool("get-camtable")

        if not netdev.primary_name:
            hostname = netdev.label
        elif netdev.primary_name.fqdn.dns_domain.name == 'ms.com':
            hostname = netdev.primary_name.fqdn.name
        else:
            hostname = netdev.fqdn
        args = []

        if ssh_args:
            args.extend(ssh_args)
        # TODO debug options shows CheckNet fails to return data and not
        # get-camtable
        args.extend([importer, "--debug", hostname])

        try:
            out = run_command(args)
        except ProcessException as err:
            raise ArgumentError("Failed to run network device discovery: %s" % err)

        macports = JSONDecoder().decode(out)
        validate_json(self.config, macports, "discovered_macs",
                      "discovered MACs")
        for (mac, port) in macports:
            update_or_create_observed_mac(session, netdev, port,
                                          MACAddress(mac), now)

    def clear(self, session, netdev):
        session.query(ObservedMac).filter_by(network_device=netdev).delete()
        session.flush()

    def poll_vlan(self, session, logger, netdev, now, ssh_args):
        if not netdev.primary_ip:
            raise ArgumentError("Cannot poll VLAN info for {0:l} without "
                                "a registered IP address.".format(netdev))
        del netdev.port_groups[:]
        session.flush()

        # Restrict operations to the internal network
        dbnet_env = NetworkEnvironment.get_unique_or_default(session)

        args = []
        if ssh_args:
            args.extend(ssh_args)
        args.append(self.config.lookup_tool("vlan2net"))
        args.append("-ip")
        args.append(netdev.primary_ip)
        out = run_command(args)

        try:
            reader = DictReader(StringIO(out))
            for row in reader:
                vlan = row.get("vlan", None)
                network = row.get("network", None)
                bitmask = row.get("bitmask", None)
                if vlan is None or network is None or bitmask is None or \
                   len(vlan) == 0 or len(network) == 0 or len(bitmask) == 0:
                    logger.client_info("Missing value for vlan, network or "
                                       "bitmask in output line #%d: %s",
                                       reader.line_num, row)
                    continue
                try:
                    vlan_int = int(vlan)
                except ValueError as e:
                    logger.client_info("Error parsing vlan number in output "
                                       "line #%d: %s error: %s",
                                       reader.line_num, row, e)
                    continue
                try:
                    network = force_ipv4("network", network)
                except ArgumentError as e:
                    logger.client_info(str(e))
                    continue
                try:
                    bitmask_int = int(bitmask)
                except ValueError as e:
                    logger.client_info("Error parsing bitmask in output "
                                       "line #%d: %s error: %s",
                                       reader.line_num, row, e)
                    continue
                dbnetwork = Network.get_unique(session, ip=network,
                                               network_environment=dbnet_env)
                if not dbnetwork:
                    logger.client_info("Unknown network %s in output "
                                       "line #%d: %s",
                                       network, reader.line_num, row)
                    continue
                if dbnetwork.cidr != bitmask_int:
                    logger.client_info("{0}: skipping VLAN {1}, because network "
                                       "bitmask value {2} differs from prefixlen "
                                       "{3.cidr} of {3:l}.".format(netdev, vlan,
                                                                   bitmask,
                                                                   dbnetwork))
                    continue

                dbvi = VlanInfo.get_unique(session, vlan_id=vlan_int,
                                           compel=False)
                if not dbvi:
                    logger.client_info("{0}: VLAN {1} is not defined in AQDB. "
                                       "Please use add_vlan to add it."
                                       .format(netdev, vlan_int))
                    continue

                if dbvi.vlan_type == "unknown":
                    continue

                if not dbnetwork.port_group:
                    dbnetwork.port_group = PortGroup(network_tag=vlan_int,
                                                     usage=dbvi.vlan_type,
                                                     creation_date=now)

                netdev.port_groups.append(dbnetwork.port_group)
        except CSVError as e:
            raise AquilonError("Error parsing vlan2net results: %s" % e)
