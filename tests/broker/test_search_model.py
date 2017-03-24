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
"""Module for testing the search model command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestSearchModel(TestBrokerCommand):

    def test_200_search_type_switch(self):
        command = "search model --machine_type switch"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "hp/uttorswitch", command)
        self.matchclean(out, "utchassis", command)
        self.matchclean(out, "utblade", command)

    def test_200_search_type_blade(self):
        command = "search model --machine_type blade --fullinfo"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Vendor: aurora_vendor Model: utblade", command)
        self.matchclean(out, "utchassis", command)
        self.matchclean(out, "uttorswitch", command)

    def test_200_search_vendor_hp(self):
        command = "search model --vendor hp"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "hp/uttorswitch", command)
        self.matchclean(out, "aurora_vendor", command)
        self.matchclean(out, "vmware", command)
        self.matchclean(out, "ibm", command)

    def test_200_search_vendor_ibm(self):
        command = "search model --vendor ibm"
        out = self.commandtest(command.split(" "))
        self.matchclean(out, "uttorswitch", command)

    def test_200_verifyshowall(self):
        command = "show model --all"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Vendor: hp Model: uttorswitch", command)

    def test_200_verify_utchassis(self):
        command = "show model --model utchassis"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Vendor: aurora_vendor Model: utchassis", command)
        self.matchoutput(out, "Model Type: chassis", command)

    def test_200_verify_utchassis_proto(self):
        command = "show model --model utchassis --format proto"
        model = self.protobuftest(command.split(" "), expect=1)[0]
        self.assertEqual(model.name, "utchassis")
        self.assertEqual(model.vendor, "aurora_vendor")
        self.assertEqual(model.model_type, "chassis")

    def test_200_verify_utblade(self):
        command = "show model --model utblade"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Vendor: aurora_vendor Model: utblade", command)
        self.matchoutput(out, "Model Type: blade", command)

    def test_200_verify_utblade_proto(self):
        command = "show model --model utblade --format proto"
        model = self.protobuftest(command.split(" "), expect=1)[0]
        self.assertEqual(model.name, "utblade")
        self.assertEqual(model.vendor, "aurora_vendor")
        self.assertEqual(model.model_type, "blade")

    def test_200_verify_utmedium(self):
        command = "show model --model utmedium"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Vendor: utvendor Model: utmedium", command)
        self.matchoutput(out, "Model Type: virtual_machine", command)
        self.matchoutput(out, "NIC Vendor: utvirt Model: default", command)

    def test_200_verify_utmedium_proto(self):
        command = "show model --model utmedium --format proto"
        model = self.protobuftest(command.split(" "), expect=1)[0]
        self.assertEqual(model.name, "utmedium")
        self.assertEqual(model.vendor, "utvendor")
        self.assertEqual(model.model_type, "virtual_machine")

    def test_200_verifyaddutccissmodel(self):
        command = "show model --model utccissmodel"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Vendor: hp Model: utccissmodel", command)
        self.matchoutput(out, "Model Type: rackmount", command)
        self.matchoutput(out, "MachineSpecs for hp utccissmodel", command)
        self.matchoutput(out, "Cpu: e5-2640 x 2", command)
        self.matchoutput(out, "Memory: 49152 MB", command)
        self.matchoutput(out, "Disk: c0d0 466 GB cciss (local)",
                         command)

    def test_200_search_nic_vendor_model(self):
        command = ["search_model", "--nicvendor", "utvirt",
                   "--nicmodel", "default"]
        out = self.commandtest(command)
        self.matchoutput(out, "utvendor/utmedium", command)
        self.matchclean(out, "utlarge", command)

    def test_200_search_fullinfo(self):
        command = ["search_model", "--diskcontroller", "cciss", "--fullinfo"]
        out = self.commandtest(command)
        self.matchoutput(out, "Vendor: hp Model: utccissmodel", command)
        self.matchoutput(out, "Model Type: rackmount", command)
        self.matchoutput(out, "MachineSpecs for hp utccissmodel", command)
        self.matchoutput(out, "Cpu: e5-2640 x 2", command)
        self.matchoutput(out, "Memory: 49152 MB", command)
        self.matchoutput(out, "Disk: c0d0 466 GB cciss (local)",
                         command)

    def test_200_search_cpu_count(self):
        command = ["search_model", "--cpunum", "2"]
        out = self.commandtest(command)
        self.matchoutput(out, "hs21-8853", command)
        self.matchoutput(out, "bl460cg8", command)
        self.matchoutput(out, "r730", command)
        self.matchclean(out, "f5_model", command)
        self.matchclean(out, "uttorswitch", command)
        self.matchclean(out, "utchassis", command)

    def test_200_search_memory(self):
        command = ["search_model", "--memory", "16384"]
        out = self.commandtest(command)
        self.matchoutput(out, "utlarge", command)
        self.matchclean(out, "hs21-8853", command)
        self.matchclean(out, "bl460cg8", command)
        self.matchclean(out, "f5_model", command)
        self.matchclean(out, "uttorswitch", command)
        self.matchclean(out, "utchassis", command)

    def test_200_search_disk_type(self):
        command = ["search_model", "--disktype", "virtual_disk"]
        out = self.commandtest(command)
        self.matchoutput(out, "utmedium", command)
        self.matchoutput(out, "utlarge", command)
        self.matchclean(out, "hs21-8853", command)
        self.matchclean(out, "bl460cg8", command)
        self.matchclean(out, "f5_model", command)
        self.matchclean(out, "uttorswitch", command)
        self.matchclean(out, "utchassis", command)

    def test_200_search_disk_controller(self):
        command = ["search_model", "--diskcontroller", "sata"]
        out = self.commandtest(command)
        self.matchoutput(out, "utlarge", command)
        self.matchoutput(out, "utmedium", command)
        self.matchoutput(out, "bl460cg8", command)
        self.matchclean(out, "utccissmodel", command)
        self.matchclean(out, "hs21-8853", command)
        self.matchclean(out, "f5_model", command)
        self.matchclean(out, "uttorswitch", command)
        self.matchclean(out, "utchassis", command)

    def test_200_search_disk_size(self):
        command = ["search_model", "--disksize", "600"]
        out = self.commandtest(command)
        self.matchoutput(out, "hp/dl360g9", command)
        self.matchoutput(out, "dell/r730", command)
        self.matchclean(out, "utlarge", command)
        self.matchclean(out, "utmedium", command)
        self.matchclean(out, "utccissmodel", command)
        self.matchclean(out, "hs21-8853", command)
        self.matchclean(out, "f5_model", command)
        self.matchclean(out, "utchassis", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchModel)
    unittest.TextTestRunner(verbosity=2).run(suite)
