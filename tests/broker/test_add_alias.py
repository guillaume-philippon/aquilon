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
"""Module for testing the add/show alias command."""

import unittest

if __name__ == '__main__':
    from broker import utils
    utils.import_depends()

from broker.brokertest import TestBrokerCommand
from eventstest import EventsTestMixin


class TestAddAlias(EventsTestMixin, TestBrokerCommand):
    def test_100_add_alias2host(self):
        self.event_add_dns('alias2host.aqd-unittest.ms.com')
        cmd = ['add', 'alias', '--fqdn', 'alias2host.aqd-unittest.ms.com',
               '--target', 'arecord13.aqd-unittest.ms.com']
        self.noouttest(cmd)
        self.events_verify()

    def test_105_add_aliasduplicate(self):
        cmd = ['add', 'alias', '--fqdn', 'alias2host.aqd-unittest.ms.com',
               '--target', 'arecord13.aqd-unittest.ms.com']
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Alias alias2host.aqd-unittest.ms.com "
                         "already exists.", cmd)

    def test_110_mscom_alias(self):
        self.event_add_dns('alias.ms.com')
        cmd = ['add', 'alias', '--fqdn', 'alias.ms.com',
               '--target', 'arecord13.aqd-unittest.ms.com',
               '--comments', 'Some alias comments']
        self.dsdb_expect("add_host_alias "
                         "-host_name arecord13.aqd-unittest.ms.com "
                         "-alias_name alias.ms.com "
                         "-comments Some alias comments")
        self.noouttest(cmd)
        self.dsdb_verify()
        self.events_verify()

    def test_120_conflict_a_record(self):
        cmd = ['add', 'alias', '--fqdn', 'arecord14.aqd-unittest.ms.com',
               '--target', 'arecord13.aqd-unittest.ms.com']
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "DNS Record arecord14.aqd-unittest.ms.com "
                         "already exists.", cmd)

    def test_130_conflict_reserver_name(self):
        cmd = ['add', 'alias', '--fqdn', 'nyaqd1.ms.com',
               '--target', 'arecord13.aqd-unittest.ms.com']
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Reserved Name nyaqd1.ms.com already exists.", cmd)

    def test_140_restricted_domain(self):
        cmd = ["add", "alias", "--fqdn", "foo.restrict.aqd-unittest.ms.com",
               "--target", "arecord13.aqd-unittest.ms.com"]
        out = self.badrequesttest(cmd)
        self.matchoutput(out,
                         "DNS Domain restrict.aqd-unittest.ms.com is "
                         "restricted, aliases are not allowed.",
                         cmd)

    def test_150_add_alias2diff_environment(self):
        self.event_add_dns('alias2host.aqd-unittest-ut-env.ms.com', dns_enviornment='ut-env')
        cmd = ['add', 'alias', '--fqdn', 'alias2host.aqd-unittest-ut-env.ms.com',
               '--dns_environment', 'ut-env',
               '--target', 'arecord13.aqd-unittest.ms.com',
               '--target_environment', 'internal']
        self.noouttest(cmd)
        self.events_verify()

    def test_155_add_alias2explicit_target_environment(self):
        cmd = ['add', 'alias', '--fqdn', 'alias2alias.aqd-unittest-ut-env.ms.com',
               '--dns_environment', 'ut-env',
               '--target', 'alias2host.aqd-unittest-ut-env.ms.com',
               '--target_environment', 'ut-env']
        self.noouttest(cmd)

    def test_160_add_alias_with_fqdn_in_diff_environment(self):
        cmd = ['add', 'alias', '--fqdn', 'alias13.aqd-unittest.ms.com',
               '--dns_environment', 'ut-env',
               '--target', 'arecord13.aqd-unittest.ms.com',
               '--target_environment', 'internal']
        self.noouttest(cmd)

    def test_200_autocreate_target(self):
        cmd = ["add", "alias", "--fqdn", "restrict1.aqd-unittest.ms.com",
               "--target", "target.restrict.aqd-unittest.ms.com"]
        out = self.statustest(cmd)
        self.matchoutput(out,
                         "WARNING: Will create a reference to "
                         "target.restrict.aqd-unittest.ms.com, but ",
                         cmd)

    def test_201_verify_autocreate(self):
        cmd = ["search", "dns", "--fullinfo",
               "--fqdn", "target.restrict.aqd-unittest.ms.com"]
        out = self.commandtest(cmd)
        self.matchoutput(out,
                         "Reserved Name: target.restrict.aqd-unittest.ms.com",
                         cmd)

    def test_201_verify_noprimary(self):
        cmd = ["search", "dns", "--noprimary_name",
               "--record_type", "reserved_name"]
        out = self.commandtest(cmd)
        self.matchoutput(out, "target.restrict.aqd-unittest.ms.com", cmd)

    def test_210_autocreate_second_alias(self):
        cmd = ["add", "alias", "--fqdn", "restrict2.aqd-unittest.ms.com",
               "--target", "target.restrict.aqd-unittest.ms.com"]
        self.noouttest(cmd)

    def test_220_restricted_alias_no_dsdb(self):
        cmd = ["add", "alias", "--fqdn", "restrict.ms.com",
               "--target", "no-dsdb.restrict.aqd-unittest.ms.com"]
        out = self.statustest(cmd)
        self.matchoutput(out,
                         "WARNING: Will create a reference to "
                         "no-dsdb.restrict.aqd-unittest.ms.com, but ",
                         cmd)
        self.dsdb_verify(empty=True)

    def test_400_verify_alias2host(self):
        cmd = "show alias --fqdn alias2host.aqd-unittest.ms.com"
        out = self.commandtest(cmd.split(" "))

        self.matchoutput(out, "Alias: alias2host.aqd-unittest.ms.com", cmd)
        self.matchoutput(out, "Target: arecord13.aqd-unittest.ms.com", cmd)
        self.matchoutput(out, "DNS Environment: internal", cmd)

    def test_405_verify_host_shows_alias(self):
        cmd = "show address --fqdn arecord13.aqd-unittest.ms.com"
        out = self.commandtest(cmd.split(" "))
        self.matchoutput(out, "Aliases: alias.ms.com, "
                         "alias13.aqd-unittest.ms.com [environment: ut-env], "
                         "alias2alias.aqd-unittest-ut-env.ms.com [environment: ut-env], "
                         "alias2host.aqd-unittest-ut-env.ms.com [environment: ut-env], "
                         "alias2host.aqd-unittest.ms.com", cmd)

    def test_410_verify_mscom_alias(self):
        cmd = "show alias --fqdn alias.ms.com"
        out = self.commandtest(cmd.split(" "))

        self.matchoutput(out, "Alias: alias.ms.com", cmd)
        self.matchoutput(out, "Target: arecord13.aqd-unittest.ms.com", cmd)
        self.matchoutput(out, "DNS Environment: internal", cmd)
        self.matchoutput(out, "Comments: Some alias comments", cmd)

    def test_420_verify_alias2diff_environment(self):
        cmd = "show alias --fqdn alias2host.aqd-unittest-ut-env.ms.com --dns_environment ut-env"
        out = self.commandtest(cmd.split(" "))
        self.matchoutput(out, "Alias: alias2host.aqd-unittest-ut-env.ms.com", cmd)
        self.matchoutput(out, "Target: arecord13.aqd-unittest.ms.com [environment: internal]", cmd)
        self.matchoutput(out, "DNS Environment: ut-env", cmd)

    def test_425_verify_alias2alias_with_diff_environment(self):
        cmd = "show alias --fqdn alias2alias.aqd-unittest-ut-env.ms.com --dns_environment ut-env"
        out = self.commandtest(cmd.split(" "))
        self.matchoutput(out, "Alias: alias2alias.aqd-unittest-ut-env.ms.com", cmd)
        self.matchoutput(out, "Target: alias2host.aqd-unittest-ut-env.ms.com", cmd)
        self.matchoutput(out, "DNS Environment: ut-env", cmd)

    def test_500_add_alias2alias(self):
        cmd = ['add', 'alias', '--fqdn', 'alias2alias.aqd-unittest.ms.com',
               '--target', 'alias2host.aqd-unittest.ms.com', '--ttl', 60]
        self.noouttest(cmd)

    def test_510_add_alias3alias(self):
        cmd = ['add', 'alias', '--fqdn', 'alias3alias.aqd-unittest.ms.com',
               '--target', 'alias2alias.aqd-unittest.ms.com']
        self.noouttest(cmd)

    def test_520_add_alias4alias(self):
        cmd = ['add', 'alias', '--fqdn', 'alias4alias.aqd-unittest.ms.com',
               '--target', 'alias3alias.aqd-unittest.ms.com']
        self.noouttest(cmd)

    def test_530_add_alias5alias_fail(self):
        cmd = ['add', 'alias', '--fqdn', 'alias5alias.aqd-unittest.ms.com',
               '--target', 'alias4alias.aqd-unittest.ms.com']
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Maximum alias depth exceeded", cmd)

    def test_600_verify_alias2alias(self):
        cmd = 'show alias --fqdn alias2alias.aqd-unittest.ms.com'
        out = self.commandtest(cmd.split(" "))
        self.matchoutput(out, 'Alias: alias2alias.aqd-unittest.ms.com', cmd)
        self.matchoutput(out, 'TTL: 60', cmd)

    def test_601_verify_alias2alias_backwards(self):
        cmd = 'show alias --fqdn alias2host.aqd-unittest.ms.com'
        out = self.commandtest(cmd.split(" "))
        self.matchoutput(out, "Aliases: alias2alias.aqd-unittest.ms.com", cmd)

    def test_602_verify_alias2alias_recursive(self):
        cmd = 'show address --fqdn arecord13.aqd-unittest.ms.com'
        out = self.commandtest(cmd.split(" "))
        self.matchoutput(out,
                         "Aliases: alias.ms.com, "
                         "alias13.aqd-unittest.ms.com [environment: ut-env], "
                         "alias2alias.aqd-unittest-ut-env.ms.com [environment: ut-env], "
                         "alias2alias.aqd-unittest.ms.com, "
                         "alias2host.aqd-unittest-ut-env.ms.com [environment: ut-env], "
                         "alias2host.aqd-unittest.ms.com, "
                         "alias3alias.aqd-unittest.ms.com, "
                         "alias4alias.aqd-unittest.ms.com",
                         cmd)

    def test_700_show_alias_host(self):
        ip = self.net["zebra_eth0"].usable[0]
        command = ["add", "alias", "--fqdn", "alias0.aqd-unittest.ms.com",
                   "--target", "unittest20-e0.aqd-unittest.ms.com"]
        out = self.commandtest(command)

        command = ["add", "alias", "--fqdn", "alias01.aqd-unittest.ms.com",
                   "--target", "alias0.aqd-unittest.ms.com"]
        out = self.commandtest(command)

        command = ["show", "host", "--hostname", "unittest20.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Provides: unittest20-e0.aqd-unittest.ms.com \[%s\]\s*'
                          r'Aliases: alias0.aqd-unittest.ms.com, alias01.aqd-unittest.ms.com'
                          % ip,
                          command)

        command = ["show", "host", "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--format", "proto"]
        host = self.protobuftest(command, expect=1)[0]
        self.assertEqual(host.hostname, 'unittest20')
        interfaces = {iface.device: iface for iface in host.machine.interfaces}
        self.assertIn("eth0", interfaces)
        self.assertEqual(interfaces["eth0"].aliases[0], 'alias0.aqd-unittest.ms.com')
        self.assertEqual(interfaces["eth0"].aliases[1], 'alias01.aqd-unittest.ms.com')
        self.assertEqual(interfaces["eth0"].ip, str(ip))
        self.assertEqual(interfaces["eth0"].fqdn, 'unittest20-e0.aqd-unittest.ms.com')

        command = ["del", "alias", "--fqdn", "alias01.aqd-unittest.ms.com"]
        out = self.commandtest(command)

        command = ["del", "alias", "--fqdn", "alias0.aqd-unittest.ms.com"]
        out = self.commandtest(command)

    def test_710_show_alias_host(self):
        ip = self.net["zebra_eth1"].usable[3]
        command = ["add", "alias", "--fqdn", "alias1.aqd-unittest.ms.com",
                   "--target", "unittest20-e1-1.aqd-unittest.ms.com"]
        out = self.commandtest(command)

        command = ["add", "alias", "--fqdn", "alias11.aqd-unittest.ms.com",
                   "--target", "alias1.aqd-unittest.ms.com"]
        out = self.commandtest(command)

        command = ["show", "host", "--hostname", "unittest20.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Provides: unittest20-e1-1.aqd-unittest.ms.com \[%s\] \(label: e1\)\s*'
                          r'Aliases: alias1.aqd-unittest.ms.com, alias11.aqd-unittest.ms.com'
                          % ip,
                          command)

        command = ["show", "host", "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--format", "proto"]
        host = self.protobuftest(command, expect=1)[0]
        self.assertEqual(host.hostname, 'unittest20')
        interfaces = {iface.device: iface for iface in host.machine.interfaces}
        self.assertIn("eth1:e1", interfaces)
        self.assertEqual(interfaces["eth1:e1"].aliases[0], 'alias1.aqd-unittest.ms.com')
        self.assertEqual(interfaces["eth1:e1"].aliases[1], 'alias11.aqd-unittest.ms.com')
        self.assertEqual(interfaces["eth1:e1"].ip, str(ip))
        self.assertEqual(interfaces["eth1:e1"].fqdn, 'unittest20-e1-1.aqd-unittest.ms.com')

        command = ["del", "alias", "--fqdn", "alias11.aqd-unittest.ms.com"]
        out = self.commandtest(command)

        command = ["del", "alias", "--fqdn", "alias1.aqd-unittest.ms.com"]
        out = self.commandtest(command)

    def test_800_grn(self):
        command = ["add", "alias",
                   "--fqdn", "alias2host-grn.aqd-unittest.ms.com",
                   "--target", "arecord50.aqd-unittest.ms.com",
                   "--grn", "grn:/ms/ei/aquilon/aqd"]
        self.noouttest(command)

    def test_805_verify_grn(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "alias2host-grn.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Owned by GRN: grn:/ms/ei/aquilon/aqd",
                         command)

    def test_810_eon_id(self):
        command = ["add", "alias",
                   "--fqdn", "alias2host-eon-id.aqd-unittest.ms.com",
                   "--target", "arecord51.aqd-unittest.ms.com",
                   "--eon_id", "3"]
        self.noouttest(command)

    def test_815_verify_eon_id(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "alias2host-eon-id.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Owned by GRN: grn:/ms/ei/aquilon/unittest",
                         command)

    def test_850_grn_conflict_with_primary_name(self):
        command = ["add", "alias",
                   "--fqdn", "alias2host-bad-target.aqd-unittest.ms.com",
                   "--target", "unittest00.one-nyp.ms.com",
                   "--grn", "grn:/ms/ei/aquilon/unittest"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Alias alias2host-bad-target.aqd-unittest.ms.com "
                         "depends on DNS Record unittest00.one-nyp.ms.com. "
                         "It conflicts with GRN grn:/ms/ei/aquilon/unittest: "
                         "DNS Record unittest00.one-nyp.ms.com is a primary "
                         "name. GRN should not be set but derived from the "
                         "device.",
                         command)

    def test_860_grn_conflict_with_service_address(self):
        command = ["add", "alias",
                   "--fqdn", "alias2host-bad-target.aqd-unittest.ms.com",
                   "--target", "zebra2.aqd-unittest.ms.com",
                   "--grn", "grn:/ms/ei/aquilon/unittest"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Alias alias2host-bad-target.aqd-unittest.ms.com "
                         "depends on DNS Record zebra2.aqd-unittest.ms.com. "
                         "It conflicts with GRN grn:/ms/ei/aquilon/unittest: "
                         "DNS Record zebra2.aqd-unittest.ms.com is a service "
                         "address. GRN should not be set but derived from the "
                         "device.",
                         command)

    def test_870_grn_conflict_with_interface_address(self):
        command = ["add", "alias",
                   "--fqdn", "alias2host-bad-target.aqd-unittest.ms.com",
                   "--target", "unittest20-e1.aqd-unittest.ms.com",
                   "--grn", "grn:/ms/ei/aquilon/unittest"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Alias alias2host-bad-target.aqd-unittest.ms.com "
                         "depends on DNS Record "
                         "unittest20-e1.aqd-unittest.ms.com. "
                         "It conflicts with GRN grn:/ms/ei/aquilon/unittest: "
                         "DNS Record unittest20-e1.aqd-unittest.ms.com is "
                         "already be used by the interfaces "
                         "unittest20.aqd-unittest.ms.com/eth1. GRN should not "
                         "be set but derived from the device.",
                         command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddAlias)
    unittest.TextTestRunner(verbosity=2).run(suite)
