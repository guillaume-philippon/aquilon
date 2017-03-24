#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2012,2013,2015,2016  Contributor
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
"""Module for testing the update service command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestUpdateService(TestBrokerCommand):

    def test_100_updateafsservice(self):
        command = ["update_service", "--service", "afs", "--max_clients", 2500,
                   "--comments", "New service comments"]
        self.noouttest(command)

    def test_101_update_instance_comments(self):
        command = ["update_service", "--service", "afs", "--instance", "q.ny.ms.com",
                   "--comments", "New instance comments"]
        self.noouttest(command)

    def test_105_verifyupdateafsservice(self):
        command = "show service --service afs"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: afs", command)
        self.matchoutput(out, "Default Maximum Client Count: 2500", command)
        self.matchoutput(out, "Service: afs Instance: q.ny", command)
        self.matchoutput(out, "Maximum Client Count: Default (2500)", command)
        self.searchoutput(out, "^  Comments: New service comments", command)
        self.searchoutput(out,
                          r'Service: afs Instance: q\.ny\.ms\.com$\n'
                          r'(    .*$\n)+'
                          r'^    Comments: New instance comments',
                          command)

    def test_105_verify_instance_comment(self):
        command = ["show_service", "--service", "afs", "--instance", "q.ny.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "New instance comments", command)
        self.matchclean(out, "New service comments", command)

    def test_110_preverifybootserverservice(self):
        command = "show service --service bootserver"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: bootserver", command)
        self.matchoutput(out, "Default Maximum Client Count: Unlimited",
                         command)
        self.matchoutput(out, "Service: bootserver Instance: one-nyp", command)
        self.matchoutput(out, "Maximum Client Count: Default (Unlimited)",
                         command)

    def test_111_updatebootserverservice(self):
        command = "update service --service bootserver --default"
        self.noouttest(command.split(" "))

    def test_115_verifyupdatebootserverservice(self):
        command = "show service --service bootserver"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: bootserver", command)
        self.matchoutput(out, "Default Maximum Client Count: Unlimited",
                         command)
        self.matchoutput(out, "Service: bootserver Instance: one-nyp", command)
        self.matchoutput(out, "Maximum Client Count: Default (Unlimited)",
                         command)

    def test_120_updatebootserverinstance(self):
        command = ["update_service", "--service=bootserver",
                   "--instance=one-nyp", "--max_clients=1000"]
        self.noouttest(command)

    def test_125_verifyupdatebootserverservice(self):
        command = "show service --service bootserver"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: bootserver", command)
        self.matchoutput(out, "Default Maximum Client Count: Unlimited",
                         command)
        self.matchoutput(out, "Service: bootserver Instance: one-nyp", command)
        self.matchoutput(out, "Maximum Client Count: 1000", command)

    def test_130_updateutsvc(self):
        command = "update service --service utsvc --max_clients 1000"
        self.noouttest(command.split(" "))

    def test_131_updateutsi1(self):
        command = ["update_service", "--service=utsvc", "--instance=utsi1",
                   "--max_clients=900"]
        self.noouttest(command)

    def test_132_verifyupdateutsvc(self):
        command = "show service --service utsvc"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: utsvc", command)
        self.matchoutput(out, "Default Maximum Client Count: 1000", command)
        self.matchoutput(out, "Service: utsvc Instance: utsi1", command)
        self.matchoutput(out, "Maximum Client Count: 900", command)
        self.matchoutput(out, "Service: utsvc Instance: utsi2", command)
        self.matchoutput(out, "Maximum Client Count: Default (1000)", command)

    def test_132_verifyupdateutsvcproto(self):
        command = ["show_service", "--service", "utsvc", "--format", "proto"]
        srv = self.protobuftest(command, expect=1)[0]
        self.assertEqual(srv.name, "utsvc")
        self.assertEqual(srv.default_max_clients, 1000)
        self.assertEqual(len(srv.serviceinstances), 2)
        for si in srv.serviceinstances:
            if si.name == "utsi1":
                self.assertEqual(si.max_clients, 900)
            else:
                self.assertEqual(si.max_clients, 0)

    def test_133_updateutsvc(self):
        command = "update service --service utsvc --max_clients 1100"
        self.noouttest(command.split(" "))

    def test_134_verifyupdateutsvc(self):
        command = "show service --service utsvc"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: utsvc", command)
        self.matchoutput(out, "Default Maximum Client Count: 1100", command)
        self.matchoutput(out, "Service: utsvc Instance: utsi1", command)
        self.matchoutput(out, "Maximum Client Count: 900", command)
        self.matchoutput(out, "Service: utsvc Instance: utsi2", command)
        self.matchoutput(out, "Maximum Client Count: Default (1100)", command)

    def test_135_updateutsvc(self):
        command = "update service --service utsvc --instance utsi1 --default"
        self.noouttest(command.split(" "))

    def test_136_verifyupdateutsvc(self):
        command = "show service --service utsvc"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: utsvc", command)
        self.matchoutput(out, "Default Maximum Client Count: 1100", command)
        self.matchoutput(out, "Service: utsvc Instance: utsi1", command)
        self.matchclean(out, "Maximum Client Count: 900", command)
        self.matchoutput(out, "Service: utsvc Instance: utsi2", command)
        self.matchoutput(out, "Maximum Client Count: Default (1100)", command)

    def test_140_check_clientlist(self):
        command = ["cat", "--service", "support-group",
                   "--instance", "ec-service", "--server"]
        out = self.commandtest(command)
        self.matchclean(out, "clients", command)
        self.matchclean(out, "unittest00.one-nyp.ms.com", command)
        self.matchclean(out, "unittest02.one-nyp.ms.com", command)

    def test_141_enable_clientlist_and_aliasbindings(self):
        command = ["update_service", "--service", "support-group",
                   "--need_client_list"]
        self.noouttest(command)
        command = ["update_service", "--service", "support-group",
                   "--allow_alias_bindings"]
        self.noouttest(command)

    def test_142_check_clientlist_enabled(self):
        command = ["cat", "--service", "support-group",
                   "--instance", "ec-service", "--server"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"clients" = list\(([^)]|\s)*"unittest00.one-nyp.ms.com"',
                          command)

    def test_142_verify_service(self):
        command = ["show_service", "--service", "support-group"]
        out = self.commandtest(command)
        self.matchoutput(out, "Need Client List: True", command)
        self.matchoutput(out, "Allow Alias Bindings: True", command)

    def test_143_no_clientlist_and_aliasbindings(self):
        command = ["update_service", "--service", "support-group",
                   "--noneed_client_list"]
        self.noouttest(command)
        command = ["update_service", "--service", "support-group",
                   "--noallow_alias_bindings"]
        self.noouttest(command)

    def test_144_check_clientlist_gone(self):
        command = ["cat", "--service", "support-group",
                   "--instance", "ec-service", "--server"]
        out = self.commandtest(command)
        self.matchclean(out, "clients", command)
        self.matchclean(out, "unittest00.one-nyp.ms.com", command)
        self.matchclean(out, "unittest02.one-nyp.ms.com", command)

    def test_144_verify_service(self):
        command = ["show_service", "--service", "support-group"]
        out = self.commandtest(command)
        self.matchoutput(out, "Need Client List: False", command)
        self.matchoutput(out, "Allow Alias Bindings: False", command)

    # FIXME: Missing functionality and tests for plenaries.


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUpdateService)
    unittest.TextTestRunner(verbosity=2).run(suite)
