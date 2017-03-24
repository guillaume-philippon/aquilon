#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013,2014,2015,2016  Contributor
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
"""Module for testing the update network command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from ipaddr import IPv4Network

from brokertest import TestBrokerCommand


class TestSplitMergeNetwork(TestBrokerCommand):

    def test_100_add_test_nets(self):
        networks = [
            # Merge various sized subnets, one is missing
            "0.2.2.0/25", "0.2.2.192/26",
            # Merge various sized subnets, first is missing
            "0.2.3.64/26", "0.2.3.128/25"
        ]
        for net in networks:
            ipnet = IPv4Network(net)
            self.noouttest(["add", "network", "--network", ipnet.ip,
                            "--ip", ipnet.ip, "--prefixlen", ipnet.prefixlen,
                            "--building", "nettest", "--side", "b",
                            "--comments", "Original %s" % ipnet])

            self.check_plenary_exists("network", "internal", str(ipnet.ip),
                                      "config")

    def test_110_add_dns_records(self):
        self.dsdb_expect_add("merge1.aqd-unittest.ms.com", "0.2.2.200")
        self.noouttest(["add", "address", "--ip", "0.2.2.200",
                        "--fqdn", "merge1.aqd-unittest.ms.com"])
        self.dsdb_expect_add("merge2.aqd-unittest.ms.com", "0.2.3.192")
        self.noouttest(["add", "address", "--ip", "0.2.3.192",
                        "--fqdn", "merge2.aqd-unittest.ms.com"])
        self.dsdb_verify()

    def test_120_add_routers(self):
        self.noouttest(["add", "router", "address", "--ip", "0.2.2.1",
                        "--fqdn", "rtr1-merge1.aqd-unittest.ms.com"])
        self.noouttest(["add", "router", "address", "--ip", "0.2.2.193",
                        "--fqdn", "rtr2-merge1.aqd-unittest.ms.com"])
        self.noouttest(["add", "router", "address", "--ip", "0.2.3.129",
                        "--fqdn", "rtr1-merge2.aqd-unittest.ms.com"])

    def test_200_merge1(self):
        command = ["merge", "network", "--ip", "0.2.2.0",
                   "--netmask", "255.255.255.0"]
        self.noouttest(command)

        self.check_plenary_exists("network", "internal", "0.2.2.0", "config")
        self.check_plenary_gone("network", "internal", "0.2.2.192", "config")

    def test_210_supernet1(self):
        command = ["show", "network", "--ip", "0.2.2.0"]
        out = self.commandtest(command)
        self.matchoutput(out, "Netmask: 255.255.255.0", command)
        self.matchoutput(out, "Routers: 0.2.2.1 (None)", command)

        command = ["cat", "--networkip", "0.2.2.0"]
        out = self.commandtest(command)
        self.matchoutput(out, '"netmask" = "255.255.255.0";', command)
        self.matchoutput(out, '"broadcast" = "0.2.2.255";', command)
        self.matchoutput(out, '"prefix_length" = 24;', command)

    def test_211_subnet1_gone(self):
        self.notfoundtest(["show", "network", "--ip", "0.2.2.192"])

    def test_212_dns_record(self):
        command = ["show", "fqdn", "--fqdn", "merge1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Network: 0.2.2.0 [0.2.2.0/24]", command)

    def test_213_routers(self):
        self.notfoundtest(["show", "fqdn", "--fqdn",
                           "rtr2-merge1.aqd-unittest.ms.com"])

    def test_250_merge2(self):
        command = ["merge", "network", "--ip", "0.2.3.128", "--prefixlen", "24"]
        self.noouttest(command)

        self.check_plenary_exists("network", "internal", "0.2.3.0", "config")
        self.check_plenary_gone("network", "internal", "0.2.3.128", "config")

    def test_260_supernet2(self):
        command = ["show", "network", "--ip", "0.2.3.0"]
        out = self.commandtest(command)
        self.matchoutput(out, "Netmask: 255.255.255.0", command)
        # This is a new object; check the inherited parameters
        self.matchoutput(out, "Side: b", command)
        self.matchoutput(out, "Sysloc: nettest.ny.na", command)
        self.matchoutput(out, "Comments: Original 0.2.3.128/25", command)
        self.matchclean(out, "Routers", command)

        command = ["cat", "--networkip", "0.2.3.0"]
        out = self.commandtest(command)
        self.matchoutput(out, '"netmask" = "255.255.255.0";', command)
        self.matchoutput(out, '"broadcast" = "0.2.3.255";', command)
        self.matchoutput(out, '"prefix_length" = 24;', command)

    def test_261_subnet2_gone(self):
        self.notfoundtest(["show", "network", "--ip", "0.2.3.64"])
        self.notfoundtest(["show", "network", "--ip", "0.2.3.128"])

    def test_262_dns_record(self):
        command = ["show", "fqdn", "--fqdn", "merge2.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        # Note that the name of the old subnet is retained
        self.matchoutput(out, "Network: 0.2.3.128 [0.2.3.0/24]", command)

    def test_263_routers(self):
        self.notfoundtest(["show", "fqdn", "--fqdn",
                           "rtr1-merge2.aqd-unittest.ms.com"])

    def test_300_split(self):
        command = ["split", "network", "--ip", "0.2.2.0", "--prefixlen", "26"]
        self.noouttest(command)

    def test_310_show_subnets(self):
        supernet = IPv4Network("0.2.2.0/24")
        idx = 2
        for subnet in supernet.subnet(new_prefix=26):
            command = ["show", "network", "--ip", subnet.ip]
            out = self.commandtest(command)
            self.matchoutput(out, "Netmask: %s" % subnet.netmask, command)
            self.matchoutput(out, "Side: b", command)
            self.matchoutput(out, "Sysloc: nettest.ny.na", command)
            if subnet.ip == supernet.ip:
                # This is the same DB object, so its comment should not change
                self.matchoutput(out, "Comments: Original 0.2.2.0/25", command)
            else:
                # Check the name
                self.matchoutput(out, "Network: 0.2.2.0_%d" % idx, command)
                idx += 1

            self.check_plenary_exists("network", "internal", str(subnet.ip),
                                      "config")

            command = ["cat", "--networkip", subnet.ip]
            out = self.commandtest(command)
            self.matchoutput(out, '"netmask" = "%s";' % subnet.netmask, command)
            self.matchoutput(out, '"broadcast" = "%s";' % subnet.broadcast, command)
            self.matchoutput(out, '"prefix_length" = 26;', command)

    def test_311_dns_record(self):
        command = ["show", "fqdn", "--fqdn", "merge1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Network: 0.2.2.0_4 [0.2.2.192/26]", command)

    def test_400_split_failure(self):
        command = ["split", "network", "--ip", "0.2.3.0", "--prefixlen", "26"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Network split failed, because the following "
                         "subnet IP and/or broadcast addresses are registered "
                         "in the DNS: 0.2.3.192", command)

    def test_900_clean_dns(self):
        self.dsdb_expect_delete("0.2.2.200")
        self.noouttest(["del", "address", "--ip", "0.2.2.200",
                        "--fqdn", "merge1.aqd-unittest.ms.com"])
        self.dsdb_expect_delete("0.2.3.192")
        self.noouttest(["del", "address", "--ip", "0.2.3.192",
                        "--fqdn", "merge2.aqd-unittest.ms.com"])
        self.dsdb_verify()

    def test_910_clean_nets(self):
        self.noouttest(["del", "network", "--ip", "0.2.2.0"])
        self.noouttest(["del", "network", "--ip", "0.2.2.64"])
        self.noouttest(["del", "network", "--ip", "0.2.2.128"])
        self.noouttest(["del", "network", "--ip", "0.2.2.192"])
        self.noouttest(["del", "network", "--ip", "0.2.3.0"])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSplitMergeNetwork)
    unittest.TextTestRunner(verbosity=2).run(suite)
