#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2016  Contributor
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
"""Module for testing the add cluster systemlist command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestAddClusterSystemList(TestBrokerCommand):

    def test_100_add_rg_single_host(self):
        self.noouttest(["add_cluster_systemlist", "--cluster", "utbvcs1b",
                        "--resourcegroup", "utbvcs1bas01",
                        "--member", "utbhost04.aqd-unittest.ms.com",
                        "--priority", 1])
        self.noouttest(["add_cluster_systemlist", "--cluster", "utbvcs1b",
                        "--resourcegroup", "utbvcs1bas02",
                        "--member", "utbhost03.aqd-unittest.ms.com",
                        "--priority", 1])

    def test_105_cat_utbvcs1b(self):
        command = ["cat", "--cluster", "utbvcs1b", "--resourcegroup", "utbvcs1bas01"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         '"resources/system_list" = append(create("resource/cluster/utbvcs1b/resourcegroup/utbvcs1bas01/system_list/system_list/config"));',
                         command)

        command = ["cat", "--cluster", "utbvcs1b", "--resourcegroup", "utbvcs1bas01",
                   "--system_list"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"members" = nlist\(\s*'
                          r'"utbhost04.aqd-unittest.ms.com", 1\s*'
                          r'\);$',
                          command)

        command = ["cat", "--cluster", "utbvcs1b", "--resourcegroup", "utbvcs1bas02",
                   "--system_list"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"members" = nlist\(\s*'
                          r'"utbhost03.aqd-unittest.ms.com", 1\s*'
                          r'\);$',
                          command)

    def test_105_show_utbvcs1b(self):
        command = ["show_cluster", "--cluster", "utbvcs1b"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Resource Group: utbvcs1bas01\s*'
                          r'(^      .*$\n)+'
                          r'^      SystemList\s*'
                          r'Member: utbhost04.aqd-unittest.ms.com Priority: 1$',
                          command)
        self.searchoutput(out,
                          r'Resource Group: utbvcs1bas02\s*'
                          r'(^      .*$\n)+'
                          r'^      SystemList\s*'
                          r'Member: utbhost03.aqd-unittest.ms.com Priority: 1$',
                          command)

    def test_105_show_utbvcs1b_proto(self):
        command = ["show_cluster", "--cluster", "utbvcs1b", "--format", "proto"]
        cluster = self.protobuftest(command, expect=1)[0]
        found = set()
        for rg in cluster.resources:
            if rg.type != "resourcegroup":
                continue
            found.add(rg.name)
            for resource in rg.resourcegroup.resources:
                if resource.type != "system_list":
                    continue
                self.assertEqual(len(resource.systemlist), 1)
                self.assertEqual(resource.systemlist[0].cluster, "utbvcs1b")
                self.assertEqual(resource.systemlist[0].rg, rg.name)
                self.assertEqual(resource.systemlist[0].priority, 1)
                if rg.name == "utbvcs1bas01":
                    self.assertEqual(resource.systemlist[0].member,
                                     "utbhost04.aqd-unittest.ms.com")
                else:
                    self.assertEqual(resource.systemlist[0].member,
                                     "utbhost03.aqd-unittest.ms.com")

        self.assertEqual(found, set(["utbvcs1bas01", "utbvcs1bas02"]))

    def test_110_cluster_default(self):
        self.noouttest(["add_cluster_systemlist", "--cluster", "utbvcs1d",
                        "--member", "utbhost07.aqd-unittest.ms.com",
                        "--priority", 5])
        self.noouttest(["add_cluster_systemlist", "--cluster", "utbvcs1d",
                        "--member", "utbhost08.aqd-unittest.ms.com",
                        "--priority", 10])

    def test_111_rg_override(self):
        # CamelCase
        self.noouttest(["add_cluster_systemlist", "--cluster", "utbvcs1d",
                        "--resourcegroup", "UTBvcs1das01",
                        "--member", "UTBhost07.aqd-unittest.ms.com",
                        "--priority", 20])
        # CamelCase
        self.noouttest(["add_cluster_systemlist", "--cluster", "utbvcs1d",
                        "--resourcegroup", "UTBvcs1das01",
                        "--member", "UTBhost08.aqd-unittest.ms.com",
                        "--priority", 15])
        self.check_plenary_exists("resource", "cluster", "utbvcs1d",
                                  "resourcegroup", "utbvcs1das01",
                                  "system_list", "system_list", "config")

    def test_115_show_utbvcs1d(self):
        command = ["show_cluster", "--cluster", "utbvcs1d"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'^    SystemList\s*'
                          r'Member: utbhost07.aqd-unittest.ms.com Priority: 5\s*'
                          r'Member: utbhost08.aqd-unittest.ms.com Priority: 10\s*',
                          command)
        self.searchoutput(out,
                          r'Resource Group: utbvcs1das01\s*'
                          r'(^      .*$\n)+'
                          r'^      SystemList\s*'
                          r'Member: utbhost08.aqd-unittest.ms.com Priority: 15\s*'
                          r'Member: utbhost07.aqd-unittest.ms.com Priority: 20\s*',
                          command)

    def test_115_show_utbvcs1d_proto(self):
        command = ["show_cluster", "--cluster", "utbvcs1d", "--format", "proto"]
        cluster = self.protobuftest(command, expect=1)[0]
        found_cluster_default = False
        found_rg_override = False
        for resource in cluster.resources:
            if resource.type == "system_list":
                found_cluster_default = True
                self.assertEqual(len(resource.systemlist), 2)
                self.assertEqual(resource.systemlist[0].cluster, "utbvcs1d")
                self.assertEqual(resource.systemlist[1].cluster, "utbvcs1d")
                self.assertEqual(resource.systemlist[0].rg, "")
                self.assertEqual(resource.systemlist[1].rg, "")
                hosts = {asl.member: asl.priority
                         for asl in resource.systemlist}
                self.assertEqual(hosts, {'utbhost07.aqd-unittest.ms.com': 5,
                                         'utbhost08.aqd-unittest.ms.com': 10})
            if resource.type == "resourcegroup" and resource.name == "utbvcs1das01":
                for res2 in resource.resourcegroup.resources:
                    if res2.type != "system_list":
                        continue
                    found_rg_override = True
                    self.assertEqual(len(res2.systemlist), 2)
                    hosts = {asl.member: asl.priority
                             for asl in res2.systemlist}
                    self.assertEqual(hosts, {'utbhost08.aqd-unittest.ms.com': 15,
                                             'utbhost07.aqd-unittest.ms.com': 20})

        self.assertTrue(found_cluster_default,
                        "cluster default settings not found")
        self.assertTrue(found_rg_override,
                        "resourcegroup override not found")

    def test_115_cat_utbvcs1d(self):
        command = ["cat", "--cluster", "utbvcs1d", "--data"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         '"system/resources/system_list" =',
                         command)

        command = ["cat", "--cluster", "utbvcs1d", "--system_list"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"members" = nlist\(\s*'
                          r'"utbhost07.aqd-unittest.ms.com", 5,\s*'
                          r'"utbhost08.aqd-unittest.ms.com", 10\s*'
                          r'\);',
                          command)

        command = ["cat", "--cluster", "utbvcs1d", "--resourcegroup",
                   "utbvcs1das01", "--system_list"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"members" = nlist\(\s*'
                          r'"utbhost07.aqd-unittest.ms.com", 20,\s*'
                          r'"utbhost08.aqd-unittest.ms.com", 15\s*'
                          r'\);',
                          command)

        command = ["cat", "--cluster", "utbvcs1d", "--resourcegroup",
                   "utbvcs1das02", "--system_list"]
        self.notfoundtest(command)

    def test_200_no_member(self):
        command = ["add_cluster_systemlist", "--cluster", "utbvcs1b",
                   "--member", "server1.aqd-unittest.ms.com", "--priority", 1]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Host server1.aqd-unittest.ms.com is not a member of "
                         "high availability cluster utbvcs1b.",
                         command)

    def test_200_add_again(self):
        command = ["add_cluster_systemlist", "--cluster", "utbvcs1b",
                   "--resourcegroup", "utbvcs1bas01",
                   "--member", "utbhost04.aqd-unittest.ms.com",
                   "--priority", 10]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Host utbhost04.aqd-unittest.ms.com already has "
                         "a(n) SystemList entry.", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddClusterSystemList)
    unittest.TextTestRunner(verbosity=2).run(suite)
