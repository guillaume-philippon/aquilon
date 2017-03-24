#!/usr/bin/env python
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
"""Module for testing the add_network command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestAddNetwork(TestBrokerCommand):

    def testaddnetwork(self):
        for network in self.net:
            if not network.autocreate:
                continue

            command = ["add_network", "--network=%s" % network.name,
                       "--ip=%s" % network.ip,
                       "--netmask=%s" % network.netmask,
                       "--" + network.loc_type, network.loc_name,
                       "--type=%s" % network.nettype,
                       "--side=%s" % network.side]
            if network.comments:
                command.extend(["--comments", network.comments])
            self.noouttest(command)

    def testverifyauroranetwork(self):
        net = self.net["aurora2"]
        command = ["show", "network", "--ip", net.ip]
        out = self.commandtest(command)
        self.matchoutput(out, "Network: aurora2", command)
        self.matchoutput(out, "IP: %s" % net.ip, command)
        self.matchoutput(out, "Network Type: %s" % net.nettype, command)
        self.matchoutput(out, "Comments: %s" % net.comments, command)
        self.matchoutput(out, "Building: np", command)

    def testverifybunker(self):
        net = self.net["np06bals03_v103"]
        command = ["show", "network", "--ip", net.ip]
        out = self.commandtest(command)
        self.matchoutput(out, "Network: np06bals03_v103", command)
        self.matchoutput(out, "IP: %s" % net.ip, command)
        self.matchoutput(out, "Bunker: nyb10.np", command)

    def testaddnetworkdup(self):
        # Old name, new address
        net = self.net["unknown0"]
        command = ["add", "network", "--network", net.name,
                   "--ip", "192.168.10.0", "--netmask", "255.255.255.0",
                   "--building", "ut", "--type", net.nettype]
        err = self.statustest(command)
        self.matchoutput(err, "WARNING: Network name %s is already used for "
                         "address %s." % (net.name, str(net)), command)

    def testaddsubnet(self):
        # Add a subnet of an existing network
        net = self.net["unknown0"]
        subnet = net.subnet()[1]
        command = ["add", "network", "--network", "subnet-test",
                   "--ip", subnet.ip, "--netmask", subnet.netmask,
                   "--building", "ut", "--type", net.nettype]
        out = self.badrequesttest(command)
        self.matchoutput(out, "IP address %s is part of existing network "
                         "named %s with address %s." %
                         (str(subnet.ip), net.name, str(net)), command)

    def testaddnetworkofcards(self):
        # An entirely fictitious network
        self.noouttest(["add_network", "--ip", "192.168.1.0",
                        "--network", "cardnetwork",
                        "--netmask", "255.255.255.0",
                        "--building", "cards", "--side", "a",
                        "--type", "unknown",
                        "--comments", "Made-up network"])

    def test_autherror_100(self):
        self.demote_current_user("operations")

    def test_autherror_200(self):
        # Another entirely fictitious network
        command = ["add_network", "--ip", "192.168.2.0",
                   "--network", "cardnetwork2", "--netmask", "255.255.255.0",
                   "--building", "cards", "--side", "a", "--type", "unknown",
                   "--comments", "Made-up network"]
        out = self.unauthorizedtest(command, auth=True, msgcheck=False)
        allowed_roles = self.config.get("site", "change_default_netenv_roles")
        role_list = allowed_roles.strip().split()
        default_ne = self.config.get("site", "default_network_environment")
        self.matchoutput(out,
                         "Only users with %s can modify networks in the %s "
                         "network environment." % (role_list, default_ne),
                         command)

    def test_autherror_300(self):
        # Yet another entirely fictitious network
        command = ["add_network", "--ip", "192.168.3.0",
                   "--network_environment", "cardenv",
                   "--network", "cardnetwork3", "--netmask", "255.255.255.0",
                   "--building", "cards", "--side", "a", "--type", "unknown",
                   "--comments", "Made-up network"]
        self.noouttest(command)

    def test_autherror_900(self):
        self.promote_current_user()

    def testaddexcx(self):
        net = self.net["unknown0"]
        subnet = net.subnet()[0]
        command = ["add", "network", "--network", "excx-net",
                   "--ip", subnet.ip, "--netmask", subnet.netmask,
                   "--building", "np", "--type", net.nettype,
                   "--network_environment", "excx"]
        self.noouttest(command)

    def testaddnetsvcmap(self):
        net = self.net["netsvcmap"]
        subnet = net.subnet()[0]
        command = ["add", "network", "--network", "netsvcmap",
                   "--ip", subnet.ip, "--netmask", subnet.netmask,
                   "--building", "ut", "--type", net.nettype]
        self.noouttest(command)

    def testaddnetperssvcmap(self):
        net = self.net["netperssvcmap"]
        subnet = net.subnet()[0]
        command = ["add", "network", "--network", "netperssvcmap",
                   "--ip", subnet.ip, "--netmask", subnet.netmask,
                   "--building", "ut", "--type", net.nettype]
        self.noouttest(command)

    def testaddutcolo(self):
        net = self.net["unknown1"]
        command = ["add", "network", "--network", "utcolo-net",
                   "--ip", net.ip, "--netmask", net.netmask,
                   "--building", "ut", "--type", net.nettype,
                   "--network_environment", "utcolo"]
        self.noouttest(command)

    def testbadip(self):
        command = ["add_network", "--ip", "10.0.0.1",
                   "--network", "bad-address", "--netmask", "255.255.255.0",
                   "--building", "ut", "--side", "a", "--type", "unknown"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "IP address 10.0.0.1 is not a network address.  "
                         "Maybe you meant 10.0.0.0?", command)

    def testshownetwork(self):
        for network in self.net:
            if not network.autocreate:
                continue

            command = "show network --ip %s" % network.ip
            out = self.commandtest(command.split(" "))
            self.matchoutput(out, "Network: %s" % network.name, command)
            self.matchoutput(out, "Network Environment: internal", command)
            self.matchoutput(out, "IP: %s" % network.ip, command)
            self.matchoutput(out, "Netmask: %s" % network.netmask, command)
            self.matchoutput(out,
                             "%s: %s" % (network.loc_type.title(),
                                         network.loc_name),
                             command)
            self.matchoutput(out, "Side: %s" % network.side, command)
            self.matchoutput(out, "Network Type: %s" % network.nettype,
                             command)

    def testshownetworkcomments(self):
        command = "show network --network np06bals03_v103"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Comments: Some network comments", command)

    def testshownetworkbuilding(self):
        command = "show_network --building ut"
        out = self.commandtest(command.split(" "))
        for network in self.net:
            if not network.autocreate:
                continue

            if ((network.loc_type == "building" and network.loc_name == "ut") or
                    (network.loc_type == "bunker" and network.loc_name == "bucket2.ut")):
                self.matchoutput(out, str(network.ip), command)
            else:
                self.matchclean(out, str(network.ip), command)

    def testshownetworkcsv(self):
        # Use --exact_location here, so we don't have to worry about networks
        # mapped to child locations
        command = "show_network --building ut --exact_location --format csv"
        out = self.commandtest(command.split(" "))
        for network in self.net:
            if not network.autocreate:
                continue
            if network.loc_type == "building" and network.loc_name == "ut":
                self.matchoutput(out, "%s,%s,%s,ut.ny.na,us,a,%s,%s\n" %
                                 (network.name, network.ip, network.netmask,
                                  network.nettype, network.comments or ""),
                                 command)
            else:
                self.matchclean(out, str(network.ip), command)

    def testshownetworkproto(self):
        command = "show network --building ut --format proto"
        self.protobuftest(command.split(" "))

    def testaddlocalnet(self):
        command = ["add", "network", "--network", "localnet", "--ip",
                   "127.0.0.0", "--netmask", "255.0.0.0",
                   "--building", "ut"]
        self.noouttest(command)

    def testshownetworknoenv(self):
        command = "show network --building np"
        out = self.commandtest(command.split(" "))
        self.matchclean(out, "excx-net", command)

        command = "show network --building ut"
        out = self.commandtest(command.split(" "))
        self.matchclean(out, "utcolo-net", command)
        self.matchoutput(out, "netsvcmap", command)
        self.matchoutput(out, "netperssvcmap", command)

    def testshownetworkwithenv(self):
        command = "show network --building np --network_environment excx"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "excx-net", command)

    def testshowexcxnoenv(self):
        command = "show network --network excx-net"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "Network excx-net not found.", command)

    def testshowexcxwithenv(self):
        net = self.net["unknown0"]
        subnet = net.subnet()[0]
        command = "show network --network excx-net --network_environment excx"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Network: excx-net", command)
        self.matchoutput(out, "Network Environment: excx", command)
        self.matchoutput(out, "IP: %s" % subnet.ip, command)
        self.matchoutput(out, "Netmask: %s" % subnet.netmask, command)

    def testshowutcolowithenv(self):
        net = self.net["unknown1"]
        command = "show network --network utcolo-net --network_environment utcolo"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Network: utcolo-net", command)
        self.matchoutput(out, "Network Environment: utcolo", command)
        self.matchoutput(out, "IP: %s" % net.ip, command)
        self.matchoutput(out, "Netmask: %s" % net.netmask, command)

    def test_800_add_utdmz1_fail(self):
        network = self.net["ut_dmz1"]
        command = ["add_network", "--network=%s" % network.name,
                   "--ip=%s" % network.ip,
                   "--netmask=%s" % network.netmask,
                   "--" + network.loc_type, network.loc_name,
                   "--type=%s" % network.nettype,
                   "--side=%s" % network.side,
                   "--network_compartment=noexistant"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Network Compartment noexistant not found.", command)

    def test_801_add_utdmz1(self):
        network = self.net["ut_dmz1"]
        command = ["add_network", "--network=%s" % network.name,
                   "--ip=%s" % network.ip,
                   "--netmask=%s" % network.netmask,
                   "--" + network.loc_type, network.loc_name,
                   "--type=%s" % network.nettype,
                   "--side=%s" % network.side,
                   "--network_compartment=perimeter.ut"]
        self.noouttest(command)

    def test_802_del_utper(self):
        command = ["del", "network", "compartment",
                   "--network_compartment", "perimeter.ut"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "still has networks defined", command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddNetwork)
    unittest.TextTestRunner(verbosity=2).run(suite)
