#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2014,2015,2016  Contributor
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
"""Module for testing parameter support for features."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from broker.brokertest import TestBrokerCommand


class TestUpdateParameterFeature(TestBrokerCommand):

    def test_100_hw_update(self):
        self.statustest(["update_parameter", "--personality", "compileserver",
                         "--archetype", "aquilon", "--feature", "bios_setup",
                         "--path", "testdefault",
                         "--value", "hardware_newstring"])

    def test_105_show_hw_params(self):
        command = ["show_parameter", "--personality", "compileserver",
                   "--archetype", "aquilon"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Hardware Feature: bios_setup\s*'
                          r'testdefault: "hardware_newstring"\s*'
                          r'testlist: \[\s*"hardware1",\s*"hardware2"\s*\]\s*',
                          command)

    def test_105_cat_hw_params(self):
        command = ["cat", "--hostname", "unittest02.one-nyp.ms.com", "--data"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"system/features/hardware/bios_setup/testboolean" = true;\s*'
                          r'"system/features/hardware/bios_setup/testdefault" = "hardware_newstring";\s*'
                          r'"system/features/hardware/bios_setup/testfalsedefault" = false;\s*'
                          r'"system/features/hardware/bios_setup/testfloat" = 100\.100;\s*'
                          r'"system/features/hardware/bios_setup/testint" = 60;\s*'
                          r'"system/features/hardware/bios_setup/testjson" = nlist\(\s*'
                          r'"key",\s*"param_key",\s*'
                          r'"values",\s*list\(\s*0\s*\)\s*\);\s*'
                          r'"system/features/hardware/bios_setup/testlist" = list\(\s*"hardware1",\s*"hardware2"\s*\);\s*'
                          r'"system/features/hardware/bios_setup/teststring" = "default";\s*',
                          command)

    def test_110_iface_update(self):
        self.noouttest(["update_parameter", "--personality", "compileserver",
                        "--archetype", "aquilon", "--feature", "src_route",
                        "--path", "testlist",
                        "--value", "newiface1,newiface2,newiface3"])

    def test_115_show_iface_params(self):
        command = ["show_parameter", "--personality", "compileserver",
                   "--archetype", "aquilon"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Interface Feature: src_route\s*'
                          r'testdefault: "interface_feature"\s*'
                          r'testlist: \[\s*"newiface1",\s*"newiface2",\s*"newiface3"\s*\]\s*',
                          command)

    def test_115_cat_iface_params(self):
        command = ["cat", "--hostname", "unittest21.aqd-unittest.ms.com", "--data"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"system/features/interface/src_route/testboolean" = true;\s*'
                          r'"system/features/interface/src_route/testdefault" = "interface_feature";\s*'
                          r'"system/features/interface/src_route/testfalsedefault" = false;\s*'
                          r'"system/features/interface/src_route/testfloat" = 100\.100;\s*'
                          r'"system/features/interface/src_route/testint" = 60;\s*'
                          r'"system/features/interface/src_route/testjson" = nlist\(\s*'
                          r'"key",\s*"param_key",\s*'
                          r'"values",\s*list\(\s*0\s*\)\s*\);\s*'
                          r'"system/features/interface/src_route/testlist" = list\(\s*"newiface1",\s*"newiface2",\s*"newiface3"\s*\);\s*'
                          r'"system/features/interface/src_route/teststring" = "default";\s*',
                          command)

    def test_120_host_update(self):
        self.noouttest(["update_parameter", "--personality", "inventory",
                        "--archetype", "aquilon", "--feature", "pre_host",
                        "--path", "testdefault", "--value", "host_newstring"])

    def test_121_update_json_array(self):
        self.noouttest(["update_parameter", "--personality", "inventory",
                        "--archetype", "aquilon", "--feature", "pre_host",
                        "--path", "testjson/values/1", "--value", 4])

    def test_121_update_json_dict(self):
        self.noouttest(["update_parameter", "--personality", "inventory",
                        "--archetype", "aquilon", "--feature", "pre_host",
                        "--path", "testjson/key", "--value", "new_key"])

    def test_125_cat_host_params(self):
        command = ["cat", "--personality", "inventory"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"/system/features/pre_host/testboolean" = false;\s*'
                          r'"/system/features/pre_host/testdefault" = "host_newstring";\s*'
                          r'"/system/features/pre_host/testfalsedefault" = false;\s*'
                          r'"/system/features/pre_host/testfloat" = 100\.100;\s*'
                          r'"/system/features/pre_host/testint" = 0;\s*'
                          r'"/system/features/pre_host/testjson" = nlist\(\s*'
                          r'"key",\s*"new_key",\s*'
                          r'"values",\s*list\(\s*1,\s*4,\s*3\s*\)\s*\);\s*'
                          r'"/system/features/pre_host/testlist" = list\(\s*"host1",\s*"host2"\s*\);\s*'
                          r'"/system/features/pre_host/teststring" = "override";\s*',
                          command)

    def test_130_upd_same_feature_name_parameter(self):
        for type in ["host", "hardware", "interface"]:
            self.statustest(["update_parameter", "--personality", "inventory",
                             "--feature", "shinynew", "--type", type,
                             "--path", "car", "--value", 'audi' + type])

    def test_135_verify_same_feature_name_parameter(self):
        command = ["show_parameter", "--personality", "inventory"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Interface Feature: shinynew\s*'
                          r'car: "audiinterface"', command)
        self.searchoutput(out,
                          r'Hardware Feature: shinynew\s*'
                          r'car: "audihardware"', command)
        self.searchoutput(out,
                          r'Host Feature: shinynew\s*'
                          r'car: "audihost"', command)

    def test_200_json_validation(self):
        command = ["update_parameter", "--archetype", "aquilon",
                   "--personality", "inventory", "--feature", "pre_host",
                   "--type", "host", "--path", "testjson",
                   "--value", '{"key": "val3", "values": []}']
        out = self.badrequesttest(command)
        self.matchoutput(out, "Failed validating", command)

    def test_200_json_validation_array_member(self):
        command = ["update_parameter", "--archetype", "aquilon",
                   "--personality", "inventory", "--feature", "pre_host",
                   "--path", "testjson/values/1", "--value", "not-an-int"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Failed validating", command)

    def test_200_json_array_index_overflow(self):
        command = ["update_parameter", "--archetype", "aquilon",
                   "--personality", "inventory", "--feature", "pre_host",
                   "--path", "testjson/values/3", "--value", 5]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "No parameter of path=testjson/values/3 defined.",
                         command)

    def test_200_json_array_index_negative(self):
        command = ["update_parameter", "--archetype", "aquilon",
                   "--personality", "inventory", "--feature", "pre_host",
                   "--path", "testjson/values/-1", "--value", 5]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Invalid list index '-1'.", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUpdateParameterFeature)
    unittest.TextTestRunner(verbosity=2).run(suite)
