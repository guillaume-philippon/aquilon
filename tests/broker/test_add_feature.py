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
"""Module for testing the add feature command."""

from collections import defaultdict
import os.path

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand

default_features = {
    "host": {
        "post_host": {
            "visibility": "public",
            "comments": "Some feature comments",
            "activation": "reboot",
            "deactivation": "reboot",
        },
        "pre_host": {
            "visibility": "public",
            "pre_personality": True,
            "activation": "reboot",
            "deactivation": "reboot",
        },
        "unused_no_params": {
            "visibility": "public",
            "comments": "Unused feature which will not have any parameters",
            "activation": "reboot",
            "deactivation": "reboot",
        },
        "shinynew": {
            "visibility": "public",
            "activation": "reboot",
            "deactivation": "reboot",
        },
    },
    "hardware": {
        "bios_setup": {
            "visibility": "public",
            "activation": "reboot",
            "deactivation": "reboot",
        },
        "shinynew": {
            "visibility": "public",
            "activation": "reboot",
            "deactivation": "reboot",
        },
    },
    "interface": {
        "src_route": {
            "visibility": "owner_only",
            "activation": "reboot",
            "deactivation": "reboot",
        },
        "shinynew": {
            "visibility": "public",
            "activation": "dispatch",
            "deactivation": "rebuild",
        },
    },
}

default_activation = ["--activation", "reboot", "--deactivation", "reboot"]


class TestAddFeature(TestBrokerCommand):

    @classmethod
    def setUpClass(cls):
        super(TestAddFeature, cls).setUpClass()

        cls.proto = cls.protocols['aqdsystems_pb2']
        desc = cls.proto.Feature.DESCRIPTOR
        cls.activation_type = desc.fields_by_name["activation"].enum_type
        cls.visibility_type = desc.fields_by_name["visibility"].enum_type

    def test_100_add_default_features(self):
        for feature_type in default_features:
            for name, params in default_features[feature_type].items():
                command = ["add_feature", "--feature", name,
                           "--type", feature_type,
                           "--grn", "grn:/ms/ei/aquilon/aqd"]
                if "visibility" in params:
                    command.extend(["--visibility", params["visibility"]])
                if "activation" in params:
                    command.extend(["--activation", params["activation"]])
                if "deactivation" in params:
                    command.extend(["--deactivation", params["deactivation"]])
                if params.get("pre_personality", False):
                    command.append("--pre_personality")
                if "comments" in params:
                    command.extend(["--comments", params["comments"]])

                self.noouttest(command)

    def test_105_verify_pre_host(self):
        command = ["show", "feature", "--feature", "pre_host", "--type", "host"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Host Feature: pre_host
              Post Personality: False
              Owned by GRN: grn:/ms/ei/aquilon/aqd
              Visibility: public
              Activation: reboot
              Deactivation: reboot
              Template: features/pre_host
            """, command)

    def test_105_verify_post_host(self):
        command = ["show", "feature", "--feature", "post_host", "--type", "host"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Host Feature: post_host
              Post Personality: True
              Owned by GRN: grn:/ms/ei/aquilon/aqd
              Visibility: public
              Activation: reboot
              Deactivation: reboot
              Template: features/post_host
              Comments: Some feature comments
            """, command)

    def test_105_verify_hw(self):
        command = ["show", "feature", "--feature", "bios_setup", "--type", "hardware"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Hardware Feature: bios_setup
              Owned by GRN: grn:/ms/ei/aquilon/aqd
              Visibility: public
              Activation: reboot
              Deactivation: reboot
              Template: features/hardware/bios_setup
            """, command)

    def test_105_verify_iface(self):
        command = ["show", "feature", "--feature", "src_route", "--type", "interface"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Interface Feature: src_route
              Owned by GRN: grn:/ms/ei/aquilon/aqd
              Visibility: owner_only
              Activation: reboot
              Deactivation: reboot
              Template: features/interface/src_route
            """, command)

    def test_120_show_all(self):
        command = ["show", "feature", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, "Host Feature: pre_host", command)
        self.matchoutput(out, "Host Feature: post_host", command)
        self.matchoutput(out, "Hardware Feature: bios_setup", command)
        self.matchoutput(out, "Interface Feature: src_route", command)
        self.matchoutput(out, "Host Feature: shinynew", command)
        self.matchoutput(out, "Hardware Feature: shinynew", command)
        self.matchoutput(out, "Interface Feature: shinynew", command)

    def test_120_show_all_proto(self):
        command = ["show", "feature", "--all", "--format", "proto"]
        result = defaultdict(dict)
        for feature in self.protobuftest(command):
            result[feature.type][feature.name] = feature

        for feature_type, features in default_features.items():
            for name, params in features.items():
                self.assertIn(name, result[feature_type])
                data = result[feature_type][name]
                self.assertEqual(data.name, name)
                self.assertEqual(data.type, feature_type)
                self.assertEqual(data.owner_eonid, 2)
                if "comments" in params:
                    self.assertEqual(data.comments, params["comments"])

                if "activation" in params:
                    val = self.activation_type.values_by_name[params["activation"].upper()]
                    self.assertEqual(data.activation, val.number)
                else:
                    self.assertEqual(data.activation, self.proto.REBOOT)
                if "deactivation" in params:
                    val = self.activation_type.values_by_name[params["deactivation"].upper()]
                    self.assertEqual(data.deactivation, val.number)
                else:
                    self.assertEqual(data.deactivation, self.proto.REBOOT)
                if "visibility" in params:
                    val = self.visibility_type.values_by_name[params["visibility"].upper()]
                    self.assertEqual(data.visibility, val.number)
                else:
                    self.assertEqual(data.visibility, data.RESRICTED)

        self.assertIn("shinynew", result["host"])
        self.assertIn("shinynew", result["hardware"])
        self.assertIn("shinynew", result["interface"])

    def test_200_pre_hw(self):
        command = ["add", "feature", "--feature", "pre_hw",
                   "--eon_id", 2, "--type", "hardware", "--pre_personality"]
        command.extend(default_activation)
        self.noouttest(command)

    def test_200_pre_iface(self):
        command = ["add", "feature", "--feature", "pre_iface",
                   "--eon_id", 2, "--type", "interface", "--pre_personality"]
        command.extend(default_activation)
        self.noouttest(command)

    def test_200_hw_prefix(self):
        command = ["add", "feature", "--feature", "hardware/host",
                   "--eon_id", 2, "--type", "host"]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "The 'hardware/' and 'interface/' prefixes "
                         "are not available for host features.", command)

    def test_200_iface_prefix(self):
        command = ["add", "feature", "--feature", "interface/host",
                   "--eon_id", 2, "--type", "host"]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "The 'hardware/' and 'interface/' prefixes "
                         "are not available for host features.", command)

    def test_200_dotdot_begin(self):
        # Use os.path.join() to test the natural path separator of the platform
        path = os.path.join("..", "foo")
        command = ["add", "feature", "--feature", path, "--type", "host",
                   "--eon_id", 2]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "Path components in the feature name must not "
                         "start with a dot.", command)

    def test_200_dotdot_middle(self):
        # Use os.path.join() to test the natural path separator of the platform
        path = os.path.join("foo", "..", "bar")
        command = ["add", "feature", "--feature", path, "--type", "host",
                   "--eon_id", 2]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "Path components in the feature name must not "
                         "start with a dot.", command)

    def test_200_hidden_begin(self):
        command = ["add", "feature", "--feature", ".foo", "--type", "host", "--eon_id", 2]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "Path components in the feature name must not "
                         "start with a dot.", command)

    def test_200_hidden_middle(self):
        command = ["add", "feature", "--feature", "foo/.bar", "--type", "host", "--eon_id", 2]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "Path components in the feature name must not "
                         "start with a dot.", command)

    def test_210_verify_post_hw(self):
        command = ["show", "feature", "--feature", "pre_hw",
                   "--type", "hardware"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Hardware Feature: pre_hw
              Owned by GRN: grn:/ms/ei/aquilon/aqd
              Visibility: restricted
              Activation: reboot
              Deactivation: reboot
              Template: features/hardware/pre_hw
            """, command)

    def test_210_verify_pre_iface(self):
        command = ["show", "feature", "--feature", "pre_iface",
                   "--type", "interface"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Interface Feature: pre_iface
              Owned by GRN: grn:/ms/ei/aquilon/aqd
              Visibility: restricted
              Activation: reboot
              Deactivation: reboot
              Template: features/interface/pre_iface
            """, command)

    def test_210_verify_hw_prefix(self):
        command = ["show", "feature", "--feature", "hardware/host",
                   "--type", "host"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Host Feature hardware/host not found.",
                         command)

    def test_210_verify_iface_prefix(self):
        command = ["show", "feature", "--feature", "interface/host",
                   "--type", "interface"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Interface Feature interface/host not found.",
                         command)

    def test_220_type_mismatch(self):
        command = ["show", "feature", "--feature", "bios_setup",
                   "--type", "host"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Host Feature bios_setup not found.",
                         command)

    def test_230_add_again(self):
        command = ["add", "feature", "--feature", "pre_host", "--type", "host", "--eon_id", 2]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "Host Feature pre_host already exists.", command)

    def test_240_add_bad_type(self):
        command = ["add", "feature", "--feature", "bad-type",
                   "--type", "no-such-type", "--eon_id", 2]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out, "Unknown feature type 'no-such-type'. The "
                         "valid values are: hardware, host, interface.",
                         command)

    def test_240_show_bad_type(self):
        command = ["show", "feature", "--feature", "bad-type",
                   "--type", "no-such-type"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Unknown feature type 'no-such-type'. The "
                         "valid values are: hardware, host, interface.",
                         command)

    def test_250_bad_visibility(self):
        command = ["add", "feature", "--feature", "bad_visibility",
                   "--eon_id", 2, "--type", "hardware",
                   "--visibility", "bad_visibility"]
        command.extend(default_activation)
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Unknown value for visibility. Valid values are: "
                         "legacy, owner_approved, owner_only, public, restricted.",
                         command)

    def test_255_bad_activation(self):
        command = ["add", "feature", "--feature", "bad_visibility",
                   "--eon_id", 2, "--type", "hardware",
                   "--visibility", "restricted",
                   "--activation", "bad_activation",
                   "--deactivation", "reboot"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Unknown value for activation. Valid values are: "
                         "dispatch, reboot, rebuild.",
                         command)

    def test_260_bad_deactivation(self):
        command = ["add", "feature", "--feature", "bad_visibility",
                   "--eon_id", 2, "--type", "hardware",
                   "--visibility", "restricted",
                   "--activation", "reboot",
                   "--deactivation", "bad_activation"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Unknown value for deactivation. Valid values are: "
                         "dispatch, reboot, rebuild.",
                         command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddFeature)
    unittest.TextTestRunner(verbosity=2).run(suite)
