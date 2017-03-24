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
"""Module for testing the add host command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand

# TODO: this file should be merged into test_add_host.py


class TestAddAquilonHost(TestBrokerCommand):
    def test_100_add_unittest00(self):
        ip = self.net["unknown0"].usable[2]
        self.dsdb_expect_add("unittest00.one-nyp.ms.com", ip, "eth0", ip.mac)
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest00.one-nyp.ms.com", "--ip", ip,
                        "--machine", "ut3c1n3", "--domain", "unittest",
                        "--personality", "inventory", "--buildstatus", "blind"])
        self.dsdb_verify()

    def test_105_show_unittest00(self):
        command = "show host --hostname unittest00.one-nyp.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out,
                         "Primary Name: unittest00.one-nyp.ms.com [%s]" %
                         self.net["unknown0"].usable[2],
                         command)
        self.matchoutput(out, "Machine: ut3c1n3", command)
        self.matchoutput(out, "Model Type: blade", command)
        self.matchoutput(out, "Archetype: aquilon", command)
        self.matchoutput(out, "Personality: inventory", command)
        self.matchoutput(out, "Domain: unittest", command)
        self.matchoutput(out, "Build Status: blind", command)
        self.matchoutput(out, "Advertise Status: False", command)
        self.matchoutput(out, "Build Status: blind", command)

    def test_105_show_unittest00_proto(self):
        command = ["show", "host", "--hostname=unittest00.one-nyp.ms.com",
                   "--format=proto"]
        host = self.protobuftest(command, expect=1)[0]
        self.assertEqual(host.hostname, 'unittest00')
        self.assertEqual(host.personality.name, 'inventory')
        self.assertEqual(host.personality.archetype.name, 'aquilon')
        self.assertEqual(host.fqdn, 'unittest00.one-nyp.ms.com')
        self.assertEqual(host.mac, self.net["unknown0"].usable[2].mac)
        self.assertEqual(host.ip, str(self.net["unknown0"].usable[2]))
        self.assertEqual(host.archetype.name, 'aquilon')
        self.assertEqual(host.dns_domain, 'one-nyp.ms.com')
        self.assertEqual(host.domain.name, 'unittest')
        self.assertEqual(host.domain.type, host.domain.DOMAIN)
        self.assertEqual(host.sandbox_author, "")
        self.assertEqual(host.status, 'blind')
        self.assertEqual(host.machine.name, 'ut3c1n3')
        self.assertEqual(host.sysloc, 'ut.ny.na')
        self.assertEqual(host.type, 'host')
        self.assertEqual(len(host.resources), 0)
        self.assertEqual(len(host.services_used), 0)
        self.assertEqual(len(host.services_provided), 0)
        self.assertEqual(host.operating_system.archetype.name, 'aquilon')
        self.assertEqual(host.operating_system.name,
                         self.config.get("archetype_aquilon",
                                         "default_osname"))
        self.assertEqual(host.operating_system.version,
                         self.config.get("archetype_aquilon",
                                         "default_osversion"))
        self.assertEqual(host.cluster, "")

    def test_110_add_unittest12(self):
        ip = self.net["unknown0"].usable[7]
        self.dsdb_expect_add("unittest12.aqd-unittest.ms.com", ip, "eth0",
                             ip.mac)
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest12.aqd-unittest.ms.com",
                        "--ip", ip, "--buildstatus", "blind",
                        "--machine", "ut3s01p1", "--domain", "unittest"])
        self.dsdb_verify()

    def test_115_show_unittest12(self):
        command = "show host --hostname unittest12.aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out,
                         "Primary Name: unittest12.aqd-unittest.ms.com [%s]" %
                         self.net["unknown0"].usable[7],
                         command)
        self.matchoutput(out, "Machine: ut3s01p1", command)
        self.matchoutput(out, "Model Type: rackmount", command)
        self.matchoutput(out, "Archetype: aquilon", command)
        self.matchoutput(out, "Personality: inventory", command)
        self.matchoutput(out, "Domain: unittest", command)
        self.matchoutput(out, "Build Status: blind", command)

    def test_130_add_unittest20_bad_iface(self):
        ip = self.net["zebra_vip"].usable[2]
        command = ["add", "host", "--archetype", "aquilon",
                   "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--ip", ip, "--zebra_interfaces", "eth0,eth2",
                   "--machine", "ut3c5n2", "--domain", "unittest",
                   "--personality", "compileserver"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Machine unittest20.aqd-unittest.ms.com does not "
                         "have an interface named eth2.", command)

    def test_130_add_unittest20_no_iface(self):
        ip = self.net["zebra_vip"].usable[2]
        command = ["add", "host", "--archetype", "aquilon",
                   "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--ip", ip, "--zebra_interfaces", ",",
                   "--machine", "ut3c5n2", "--domain", "unittest",
                   "--personality", "compileserver"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "The interface list cannot be empty.", command)

    def test_131_add_unittest20_e1(self):
        # Add the transit before the host to verify that the reverse DNS entry
        # will get fixed up
        ip = self.net["zebra_eth1"].usable[0]
        fqdn = "unittest20-e1.aqd-unittest.ms.com"
        self.dsdb_expect_delete(ip)
        self.dsdb_expect_add(fqdn, ip, "eth1", ip.mac)
        command = ["add", "interface", "address", "--machine", "ut3c5n2",
                   "--interface", "eth1", "--fqdn", fqdn]
        self.noouttest(command)
        self.dsdb_verify()

    def test_132_add_unittest20_good(self):
        ip = self.net["zebra_vip"].usable[2]
        eth1_ip = self.net["zebra_eth1"].usable[0]
        self.dsdb_expect_add("unittest20.aqd-unittest.ms.com", ip, "vip")
        self.dsdb_expect_delete(eth1_ip)
        self.dsdb_expect_add("unittest20-e1.aqd-unittest.ms.com", eth1_ip, "eth1",
                             eth1_ip.mac, primary="unittest20.aqd-unittest.ms.com")
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest20.aqd-unittest.ms.com",
                        "--ip", ip, "--zebra_interfaces", "eth0,eth1",
                        "--machine", "ut3c5n2", "--domain", "unittest",
                        "--personality", "compileserver"])
        self.dsdb_verify()

    def test_135_show_unittest20(self):
        ip = self.net["zebra_vip"].usable[2]
        eth0_ip = self.net["zebra_eth0"].usable[0]
        eth1_ip = self.net["zebra_eth1"].usable[0]
        command = ["show", "host", "--hostname",
                   "unittest20.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out, r"Interface: eth0 %s \[boot, default_route\]" %
                          eth0_ip.mac, command)
        self.searchoutput(out, r"Interface: eth1 %s \[default_route\]" %
                          eth1_ip.mac, command)
        self.searchoutput(out,
                          r"Service Address: hostname\s*"
                          r"Address: unittest20.aqd-unittest.ms.com \[%s\]\s*"
                          r"Interfaces: eth0, eth1" % ip,
                          command)
        self.matchoutput(out,
                         "Provides: unittest20-e1.aqd-unittest.ms.com [%s]" % eth1_ip,
                         command)

    def test_135_show_unittest20_proto(self):
        ip = self.net["zebra_vip"].usable[2]
        eth0_ip = self.net["zebra_eth0"].usable[0]
        eth1_ip = self.net["zebra_eth1"].usable[0]
        command = ["show", "host", "--hostname",
                   "unittest20.aqd-unittest.ms.com", "--format", "proto"]
        host = self.protobuftest(command, expect=1)[0]
        found = False
        for resource in host.resources:
            if resource.name == "hostname" and resource.type == "service_address":
                found = True
                self.assertEqual(resource.service_address.ip, str(ip))
                self.assertEqual(resource.service_address.fqdn,
                                 "unittest20.aqd-unittest.ms.com")
                ifaces = ",".join(sorted(resource.service_address.interfaces))
                self.assertEqual(ifaces, "eth0,eth1")
        self.assertTrue(found,
                        "Service address hostname not found in the resources. "
                        "Existing resources: %s" %
                        ", ".join("%s %s" % (res.type, res.name)
                                  for res in host.resources))

    def test_135_verify_unittest20_service(self):
        ip = self.net["zebra_vip"].usable[2]
        command = ["show", "service", "address", "--name", "hostname",
                   "--hostname", "unittest20.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Service Address: hostname", command)
        self.matchoutput(out, "Bound to: Host unittest20.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "Address: unittest20.aqd-unittest.ms.com [%s]" % ip,
                         command)
        self.matchoutput(out, "Interfaces: eth0, eth1", command)

    def test_135_verify_unittest20_e1(self):
        command = ["show", "address",
                   "--fqdn", "unittest20-e1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "DNS Record: unittest20-e1.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "IP: %s" % self.net["zebra_eth1"].usable[0],
                         command)
        self.matchoutput(out, "Reverse PTR: unittest20.aqd-unittest.ms.com",
                         command)

    def test_140_add_unittest21(self):
        ip = self.net["zebra_eth0"].usable[1]
        self.dsdb_expect_add("unittest21.aqd-unittest.ms.com", ip, "bond0")
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest21.aqd-unittest.ms.com",
                        "--ip", ip, "--machine", "ut3c5n3",
                        "--domain", "unittest",
                        "--personality", "compileserver",
                        "--grn", "grn:/ms/ei/aquilon/unittest"])
        self.dsdb_verify()

    def test_145_verify_unittest21_network(self):
        net = self.net["zebra_eth0"]
        ip = net.usable[1]
        command = ["show", "network", "--ip", net.ip, "--hosts",
                   "--format", "proto"]
        network = self.protobuftest(command, expect=1)[0]
        seen = False
        macs = [ip.mac]  # , self.net["zebra_eth1"].usable[1].mac]
        for host in network.hosts:
            if host.ip != str(ip):
                continue

            seen = True
            self.assertTrue(host.archetype.name == "aquilon",
                            "archetype is '%s' instead of aquilon" %
                            host.archetype.name)
            self.assertTrue(host.mac in macs,
                            "MAC is '%s' instead of %r" %
                            (host.mac, macs))
            macs.remove(host.mac)

        self.assertTrue(seen, "%s is missing from network protobuf output" % ip)

    def test_150_add_unittest22(self):
        ip = self.net["zebra_eth0"].usable[2]
        self.dsdb_expect_add("unittest22.aqd-unittest.ms.com", ip, "br0")
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest22.aqd-unittest.ms.com",
                        "--ip", ip, "--machine", "ut3c5n4",
                        "--domain", "unittest",
                        "--personality", "compileserver"])
        self.dsdb_verify()

    def test_155_verify_unittest22_network(self):
        net = self.net["zebra_eth0"]
        ip = net.usable[2]
        command = ["show", "network", "--ip", net.ip, "--hosts",
                   "--format", "proto"]
        network = self.protobuftest(command, expect=1)[0]
        seen = False
        macs = [ip.mac]  # , self.net["zebra_eth1"].usable[2].mac]
        for host in network.hosts:
            if host.ip != str(ip):
                continue

            seen = True
            self.assertTrue(host.archetype.name == "aquilon",
                            "archetype is '%s' instead of aquilon" %
                            host.archetype.name)
            self.assertTrue(host.mac in macs,
                            "MAC is '%s' instead of %r" %
                            (host.mac, macs))
            macs.remove(host.mac)

        self.assertTrue(seen, "%s is missing from network protobuf output" % ip)

    def test_160_add_unittest23(self):
        ip = self.net["vpls"].usable[1]
        self.dsdb_expect_add("unittest23.aqd-unittest.ms.com", ip, "eth0",
                             ip.mac)
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest23.aqd-unittest.ms.com",
                        "--ip", ip, "--machine", "ut3c5n5",
                        "--domain", "unittest",
                        "--personality", "compileserver"])
        self.dsdb_verify()

    def test_161_add_unittest24(self):
        ip = self.net["vpls"].usable[2]
        self.dsdb_expect_add("unittest24.aqd-unittest.ms.com", ip, "eth0",
                             ip.mac)
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest24.aqd-unittest.ms.com",
                        "--ip", ip, "--machine", "np3c5n5",
                        "--domain", "unittest",
                        "--personality", "compileserver"])
        self.dsdb_verify()

    def test_162_add_unittest25(self):
        ip = self.net["unknown0"].usable[20]
        self.dsdb_expect_add("unittest25.aqd-unittest.ms.com", ip, "eth0",
                             ip.mac)
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest25.aqd-unittest.ms.com",
                        "--ip", ip, "--machine", "ut3c5n7",
                        "--domain", "unittest",
                        "--personality", "compileserver"])
        self.dsdb_verify()

    def test_163_add_unittest26(self):
        ip = self.net["unknown0"].usable[23]
        self.dsdb_expect_add("unittest26.aqd-unittest.ms.com", ip, "eth0",
                             ip.mac)
        self.noouttest(["add", "host", "--archetype", "aquilon",
                        "--hostname", "unittest26.aqd-unittest.ms.com",
                        "--ip", ip, "--machine", "ut3c5n8",
                        "--domain", "unittest",
                        "--personality", "compileserver"])
        self.dsdb_verify()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddAquilonHost)
    unittest.TextTestRunner(verbosity=2).run(suite)
