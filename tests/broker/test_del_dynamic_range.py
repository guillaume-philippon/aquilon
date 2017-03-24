#!/usr/bin/env python
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
"""Module for testing the del dynamic range command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from ipaddr import IPv4Address

from brokertest import TestBrokerCommand


class TestDelDynamicRange(TestBrokerCommand):

    def test_100_del_different_networks(self):
        command = ["del_dynamic_range",
                   "--startip", self.net["dyndhcp0"].usable[2],
                   "--endip", self.net["dyndhcp1"].usable[2]]
        out = self.badrequesttest(command)
        self.matchoutput(out, "must be on the same subnet", command)

    # These rely on the ip never having been used...
    def test_100_del_nothing_found(self):
        command = ["del_dynamic_range",
                   "--startip", self.net["dyndhcp0"].usable[-2],
                   "--endip", self.net["dyndhcp0"].usable[-1]]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Nothing found in range", command)

    def test_100_del_nos_tart(self):
        command = ["del_dynamic_range",
                   "--startip", self.net["dyndhcp0"].usable[1],
                   "--endip", self.net["dyndhcp0"].usable[-3]]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "No system found with IP address %s" %
                         self.net["dyndhcp0"].usable[1],
                         command)

    def test_100_del_no_end(self):
        command = ["del_dynamic_range",
                   "--startip", self.net["dyndhcp0"].usable[2],
                   "--endip", self.net["dyndhcp0"].usable[-2]]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "No system found with IP address %s" %
                         self.net["dyndhcp0"].usable[-2],
                         command)

    def test_100_del_not_dynamic(self):
        command = ["del_dynamic_range",
                   "--startip", self.net["unknown0"].usable[7],
                   "--endip", self.net["unknown0"].usable[8]]
        out = self.badrequesttest(command)
        self.matchoutput(out, "The range contains non-dynamic systems",
                         command)
        self.matchoutput(out,
                         "unittest12.aqd-unittest.ms.com [%s]" %
                         self.net["unknown0"].usable[7],
                         command)
        self.matchoutput(out,
                         "unittest12r.aqd-unittest.ms.com [%s]" %
                         self.net["unknown0"].usable[8],
                         command)

    def test_200_del_range(self):
        messages = []
        for ip in range(int(self.net["dyndhcp0"].usable[2]),
                        int(self.net["dyndhcp0"].usable[-3]) + 1):
            address = IPv4Address(ip)
            self.dsdb_expect_delete(address)
            messages.append("DSDB: delete_host -ip_address %s" % address)
        command = ["del_dynamic_range",
                   "--startip", self.net["dyndhcp0"].usable[2],
                   "--endip", self.net["dyndhcp0"].usable[-3]]
        err = self.statustest(command)
        for message in messages:
            self.matchoutput(err, message, command)
        self.dsdb_verify()

    def test_210_del_end_in_range(self):
        ip = self.net["dyndhcp1"].usable[-1]
        self.dsdb_expect_delete(ip)
        command = ["del_dynamic_range", "--startip", ip, "--endip", ip]
        err = self.statustest(command)
        self.matchoutput(err, "DSDB: delete_host -ip_address %s" % ip, command)
        self.dsdb_verify()

    def test_220_clearnetwork(self):
        messages = []
        net = self.net["dyndhcp3"]
        for ip in range(int(net.usable[0]), int(net.usable[-1]) + 1):
            # One IP is missing in the middle
            if ip == int(net.usable[5]):
                continue

            address = IPv4Address(ip)
            self.dsdb_expect_delete(address)
            messages.append("DSDB: delete_host -ip_address %s" % address)
        command = ["del_dynamic_range",
                   "--clearnetwork", self.net["dyndhcp3"].ip]
        err = self.statustest(command)
        for message in messages:
            self.matchoutput(err, message, command)
        self.dsdb_verify()

    def test_221_clearnetwork_again(self):
        command = ["del_dynamic_range",
                   "--clearnetwork", self.net["dyndhcp3"].ip]
        out = self.badrequesttest(command)
        self.matchoutput(out, "No dynamic stubs found on network.", command)

    def test_300_verify_deletes(self):
        command = "search_dns --record_type=dynamic_stub"
        self.noouttest(command.split(" "))

    def test_800_cleanup_networks(self):
        self.net.dispose_network(self, "dyndhcp0")
        self.net.dispose_network(self, "dyndhcp1")
        self.net.dispose_network(self, "dyndhcp2")
        self.net.dispose_network(self, "dyndhcp3")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelDynamicRange)
    unittest.TextTestRunner(verbosity=2).run(suite)
