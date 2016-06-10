#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2012,2013,2014,2015,2016  Contributor
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

import json

if __name__ == "__main__":
    import utils
    utils.import_depends()

import unittest
from broker.brokertest import TestBrokerCommand

PERSONALITY = 'inventory'

SHOW_CMD = ["show", "parameter", "--personality", PERSONALITY]

ADD_CMD = ["add", "parameter", "--personality", PERSONALITY]

UPD_CMD = ["update", "parameter", "--personality", PERSONALITY]

DEL_CMD = ["del", "parameter", "--personality", PERSONALITY]

CAT_CMD = ["cat", "--personality", PERSONALITY]

VAL_CMD = ["validate_parameter", "--personality", PERSONALITY]


class TestParameterFeature(TestBrokerCommand):

    def test_090_verify_feature_proto_noerr(self):
        cmd = ["show", "parameter", "--personality", "utunused/dev", "--format=proto"]
        out = self.notfoundtest(cmd)
        self.matchoutput(out, "Not Found: No parameters found for personality "
                         "aquilon/utunused/dev", cmd)

    def test_100_verify_cat_host_feature_defaults(self):
        cmd = CAT_CMD + ["--pre_feature"]
        out = self.commandtest(cmd)
        self.searchoutput(out,
                          r'"/system/features/pre_host/testboolean" = true;\s*'
                          r'"/system/features/pre_host/testfalsedefault" = false;\s*'
                          r'"/system/features/pre_host/testfloat" = 100\.100;\s*'
                          r'"/system/features/pre_host/testint" = 60;\s*'
                          r'"/system/features/pre_host/testjson" = nlist\(\s*'
                          r'"key",\s*"param_key",\s*'
                          r'"values",\s*list\(\s*0\s*\)\s*\);\s*'
                          r'"/system/features/pre_host/testlist" = list\(\s*"val1",\s*"val2"\s*\);\s*'
                          r'"/system/features/pre_host/teststring" = "default";\s*',
                          cmd)

    def test_105_add_path_host_feature(self):
        path = "testdefault"
        value = "host_feature"
        cmd = ADD_CMD + ["--path", path, "--value", value, "--feature", "pre_host"]
        self.noouttest(cmd)

        path = "testlist"
        value = "host1,host2"
        cmd = ADD_CMD + ["--path", path, "--value", value, "--feature", "pre_host"]
        self.noouttest(cmd)

    def test_110_add_path_host_feature_overrides(self):
        path = "testboolean"
        value = False
        cmd = ADD_CMD + ["--path", path, "--value", value, "--feature", "pre_host"]
        self.noouttest(cmd)

        path = "teststring"
        value = "override"
        cmd = ADD_CMD + ["--path", path, "--value", value, "--feature", "pre_host"]
        self.noouttest(cmd)

        path = "testint"
        value = 0
        cmd = ADD_CMD + ["--path", path, "--value", value, "--feature", "pre_host"]
        self.noouttest(cmd)

        path = "testjson"
        value = '{"key": "other_key", "values": [1, 2]}'
        cmd = ADD_CMD + ["--path", path, "--value", value, "--feature", "pre_host"]
        self.noouttest(cmd)

    def test_115_verify_host_feature(self):
        cmd = SHOW_CMD
        out = self.commandtest(cmd)
        self.searchoutput(out,
                          r'Host Feature: pre_host\s*'
                          r'testboolean: false\s*'
                          r'testdefault: "host_feature"\s*'
                          r'testint: 0\s*'
                          r'testjson: {\s*"key":\s*"other_key",\s*"values":\s*\[\s*1,\s*2\s*\]\s*}\s*'
                          r'testlist: \[\s*"host1",\s*"host2"\s*\]\s*'
                          r'teststring: "override"\s*', cmd)

    def test_120_verify_cat_host_feature(self):
        cmd = CAT_CMD + ["--pre_feature"]
        out = self.commandtest(cmd)
        self.searchoutput(out,
                          r'"/system/features/pre_host/testboolean" = false;\s*'
                          r'"/system/features/pre_host/testdefault" = "host_feature";\s*'
                          r'"/system/features/pre_host/testfalsedefault" = false;\s*'
                          r'"/system/features/pre_host/testfloat" = 100\.100;\s*'
                          r'"/system/features/pre_host/testint" = 0;\s*'
                          r'"/system/features/pre_host/testjson" = nlist\(\s*'
                          r'"key",\s*"other_key",\s*'
                          r'"values",\s*list\(\s*1,\s*2\s*\)\s*\);\s*'
                          r'"/system/features/pre_host/testlist" = list\(\s*"host1",\s*"host2"\s*\);\s*'
                          r'"/system/features/pre_host/teststring" = "override";\s*',
                          cmd)

    # TODO: Move this to test_constraints_parameter
    def test_125_try_del_paramdef(self):
        cmd = ["del_parameter_definition", "--feature", "pre_host", "--type=host",
               "--path=testdefault"]
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Parameter with path testdefault used by following and cannot be deleted", cmd)

    def test_130_validate(self):
        cmd = VAL_CMD
        out = self.badrequesttest(cmd)

        self.searchoutput(out,
                          r'Following required parameters have not been specified:\s*',
                          cmd)
        self.searchoutput(out,
                          r'Feature Binding: pre_host\s*'
                          r'Parameter Definition: testrequired \[required\]\s*'
                          r'Type: string\s*',
                          cmd)

    def test_310_verify_feature_proto(self):
        cmd = SHOW_CMD + ["--format=proto"]
        params = self.protobuftest(cmd, expect=10)

        param_values = {}
        for param in params:
            param_values[param.path] = param.value

        self.assertEqual(set(param_values.keys()),
                         set(["espinfo/class",
                              "espinfo/function",
                              "espinfo/users",
                              "features/pre_host/testboolean",
                              "features/pre_host/testdefault",
                              "features/pre_host/testint",
                              "features/pre_host/testjson",
                              "features/pre_host/testlist",
                              "features/pre_host/teststring",
                              "windows/windows",
                             ]))

        self.assertEqual(param_values['features/pre_host/testboolean'],
                         'False')
        self.assertEqual(param_values['features/pre_host/teststring'],
                         'override')
        self.assertEqual(param_values['features/pre_host/testint'],
                         '0')

        # The order of the keys is not deterministic, so we cannot do
        # string-wise comparison here
        self.assertEqual(json.loads(param_values['features/pre_host/testjson']),
                         json.loads('{"key": "other_key", "values": [1, 2]}'))

        self.assertEqual(param_values['features/pre_host/testlist'],
                         'host1,host2')
        self.assertEqual(param_values['features/pre_host/testdefault'],
                         'host_feature')

    def test_400_json_validation(self):
        cmd = ["update_parameter", "--archetype", "aquilon",
               "--personality", PERSONALITY, "--feature", "pre_host",
               "--type", "host", "--path", "testjson",
               "--value", '{"key": "val3", "values": []}']
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Failed validating", cmd)

    def test_400_update_json_schema_value_conflict(self):
        new_schema = {
            "schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                },
                "values": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                    },
                    "maxItems": 1,
                },
            },
            "additionalProperties": False,
        }

        cmd = ["update_parameter_definition",
               "--feature", "pre_host", "--type", "host",
               "--path", "testjson", "--schema", json.dumps(new_schema)]
        out = self.badrequesttest(cmd)
        self.matchoutput(out,
                         "Existing value for personality aquilon/%s "
                         "conflicts with the new schema: [1, 2] is too long" %
                         PERSONALITY,
                         cmd)

    def test_400_update_json_schema_default_conflict(self):
        new_schema = {
            "schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                },
            },
            "additionalProperties": False,
        }

        cmd = ["update_parameter_definition",
               "--feature", "pre_host", "--type", "host",
               "--path", "testjson", "--schema", json.dumps(new_schema)]
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "The existing default value conflicts with the new schema", cmd)

    def test_500_verify_diff(self):
        cmd = ["show_diff", "--archetype", "aquilon", "--personality", PERSONALITY,
               "--other", "utpers-dev"]

        out = self.commandtest(cmd)
        self.searchoutput(out,
                          r'Differences for Parameters for host feature pre_host:\s*'
                          r'missing Parameters for host feature pre_host in Personality aquilon/utpers-dev@current:\s*'
                          r'//testboolean\s*'
                          r'//testdefault\s*'
                          r'//testint\s*'
                          r'//testjson/key\s*'
                          r'//testjson/values/0\s*'
                          r'//testjson/values/1\s*'
                          r'//testlist/0\s*'
                          r'//testlist/1\s*'
                          r'//teststring\s*',
                          cmd)

    def test_600_add_same_name_feature(self):
        feature = "shinynew"
        for type in ["host", "hardware", "interface"]:
            cmd = ["add_parameter_definition", "--feature", feature, "--type", type,
                   "--path", "car", "--value_type", "string"]
            self.noouttest(cmd)

            cmd = ["bind_feature", "--feature", feature, "--personality", PERSONALITY]
            if type == "interface":
                cmd.extend(["--interface", "eth0"])
            if type == "hardware":
                cmd.extend(["--model", "hs21-8853"])
            self.successtest(cmd)

    def test_610_add_same_name_feature_parameter(self):
        feature = "shinynew"
        path = "car"
        for type in ["host", "hardware", "interface"]:
            cmd = ADD_CMD + ["--path", path, "--value", 'bmw' + type,
                             "--feature", feature, "--type", type]
            self.successtest(cmd)

    def test_620_verify_name_feature_parameter(self):
        cmd = SHOW_CMD
        out = self.commandtest(cmd)
        self.searchoutput(out,
                          r'Interface Feature: shinynew\s*'
                          r'car: "bmwinterface"', cmd)
        self.searchoutput(out,
                          r'Hardware Feature: shinynew\s*'
                          r'car: "bmwhardware"', cmd)
        self.searchoutput(out,
                          r'Host Feature: shinynew\s*'
                          r'car: "bmwhost"', cmd)

    def test_630_upd_same_name_feature_parameter(self):
        feature = "shinynew"
        path = "car"
        for type in ["host", "hardware", "interface"]:
            cmd = UPD_CMD + ["--path", path, "--value", 'audi' + type,
                             "--feature", feature, "--type", type]
            self.successtest(cmd)

    def test_640_verify_name_feature_parameter(self):
        cmd = SHOW_CMD
        out = self.commandtest(cmd)
        self.searchoutput(out,
                          r'Interface Feature: shinynew\s*'
                          r'car: "audiinterface"', cmd)
        self.searchoutput(out,
                          r'Hardware Feature: shinynew\s*'
                          r'car: "audihardware"', cmd)
        self.searchoutput(out,
                          r'Host Feature: shinynew\s*'
                          r'car: "audihost"', cmd)

    def test_910_del_host_featue_param(self):
        cmd = DEL_CMD + ["--path=testdefault", "--feature", "pre_host"]
        self.noouttest(cmd)

    def test_950_del_same_name_feature_parameter(self):
        feature = "shinynew"
        path = "car"
        for type in ["host", "hardware", "interface"]:
            cmd = DEL_CMD + ["--path", path, "--feature", feature,
                             "--type", type]
            self.noouttest(cmd)

    def test_960_verify_same_name_feature_parameter(self):
        cmd = SHOW_CMD
        out = self.commandtest(cmd)
        self.searchclean(out, "shinynew", cmd)
        self.searchclean(out, "car", cmd)

    def test_970_unbind_same_name_feature(self):
        feature = "shinynew"
        for type in ["host", "hardware", "interface"]:
            cmd = ["unbind_feature", "--feature", feature, "--personality", PERSONALITY]
            if type == "interface":
                cmd.extend(["--interface", "eth0"])
            if type == "hardware":
                cmd.extend(["--model", "hs21-8853"])
            self.successtest(cmd)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParameterFeature)
    unittest.TextTestRunner(verbosity=2).run(suite)
