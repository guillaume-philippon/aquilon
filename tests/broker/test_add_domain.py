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
"""Module for testing the add domain command."""

import os

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestAddDomain(TestBrokerCommand):

    def test_000_fixprod(self):
        proddir = os.path.join(self.config.get("broker", "domainsdir"), "prod")
        if not os.path.exists(proddir):
            kingdir = self.config.get("broker", "kingdir")
            self.gitcommand(["clone", "--branch", "prod", kingdir, proddir])

    def test_100_add_unittest(self):
        command = ["add_domain", "--domain=unittest", "--track=utsandbox",
                   "--comments", "aqd unit test tracking domain",
                   "--disallow_manage"]
        self.successtest(command)
        self.assertTrue(os.path.exists(os.path.join(
            self.config.get("broker", "domainsdir"), "unittest")))

    def test_115_verify_unittest(self):
        command = ["show_domain", "--domain=unittest"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Domain: unittest [autosync]
              Tracking: sandbox utsandbox
              Rollback commit: None
              Validated: True
              Compiler: %(compiler)s
              Requires Change Manager: False
              May Contain Hosts/Clusters: False
              Archived: False
              Comments: aqd unit test tracking domain
            """ % {"compiler": self.config.get("panc", "pan_compiler")},
                           command)

    def test_115_verify_unittest_proto(self):
        command = ["show_domain", "--domain=unittest", "--format", "proto"]
        domain = self.protobuftest(command, expect=1)[0]
        self.assertEqual(domain.name, "unittest")
        self.assertEqual(domain.owner, "")
        self.assertEqual(domain.tracked_branch, "utsandbox")
        self.assertEqual(domain.type, domain.DOMAIN)
        self.assertEqual(domain.allow_manage, False)

    def test_110_add_utprod(self):
        command = ["add_domain", "--domain=ut-prod", "--track=prod"]
        self.successtest(command)
        self.assertTrue(os.path.exists(os.path.join(
            self.config.get("broker", "domainsdir"), "ut-prod")))

    def test_115_verify_utprod(self):
        command = ["show_domain", "--domain=ut-prod"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Domain: ut-prod [autosync]
              Tracking: domain prod
              Rollback commit: None
              Validated: True
              Compiler: %(compiler)s
              Requires Change Manager: False
              May Contain Hosts/Clusters: True
              Archived: False
            """ % {"compiler": self.config.get("panc", "pan_compiler")},
                           command)

    def test_120_add_deployable(self):
        command = ["add_domain", "--domain=deployable", "--start=prod"]
        self.successtest(command)
        self.assertTrue(os.path.exists(os.path.join(
            self.config.get("broker", "domainsdir"), "deployable")))

    def test_125_verifydeployable(self):
        command = ["show_domain", "--domain=deployable"]
        out = self.commandtest(command)
        self.matchoutput(out, "Domain: deployable", command)
        self.matchclean(out, "Tracking:", command)

    def test_130_add_leftbehind(self):
        command = ["add_domain", "--domain=leftbehind", "--start=prod"]
        self.successtest(command)

    def test_140_add_nomanage(self):
        command = ["add_domain", "--domain", "nomanage"]
        self.successtest(command)

    def test_145_verifynomanage(self):
        command = ["show_domain", "--domain=nomanage"]
        out = self.commandtest(command)
        self.matchoutput(out, "Domain: nomanage", command)
        self.matchoutput(out, "May Contain Hosts/Clusters: True", command)

    def test_150_add_unittest_xml(self):
        self.successtest(["add_domain", "--domain", "unittest-xml",
                          "--track", "utsandbox"])

    def test_150_add_unittest_json(self):
        self.successtest(["add_domain", "--domain", "unittest-json",
                          "--track", "utsandbox"])

    def test_160_add_netinfra(self):
        self.successtest(["add_domain", "--domain", "netinfra",
                          "--track", "prod"])

    def test_170_add_alt_unittest(self):
        command = ["add_domain", "--domain=alt-unittest", "--track=utsandbox",
                   "--comments", "Stuff which does not compile"]
        self.successtest(command)

    def test_210_verifysearchtrack(self):
        command = ["search", "domain", "--track", "utsandbox"]
        out = self.commandtest(command)
        self.matchoutput(out, "unittest", command)
        self.matchclean(out, "ut-prod", command)

    def test_210_verifysearchnot_tracking(self):
        command = ["search", "domain", "--not_tracking"]
        out = self.commandtest(command)
        self.matchoutput(out, "deployable", command)
        self.matchoutput(out, "leftbehind", command)
        self.matchoutput(out, "nomanage", command)
        self.searchoutput(out, r"^prod$", command)
        self.matchclean(out, "unittest", command)
        self.matchclean(out, "ut-prod", command)

    def test_210_verifysearchchm(self):
        command = ["search", "domain", "--change_manager"]
        self.noouttest(command)

    def test_300_invalidtrack(self):
        command = ["add_domain", "--domain=notvalid-prod", "--track=prod",
                   "--change_manager"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Cannot enforce a change manager for tracking domain",
                         command)

    def test_300_bad_name(self):
        command = ["add_domain", "--domain", "oops@!"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "'oops@!' is not a valid value for --domain.",
                         command)

    def test_300_bad_git_branchname(self):
        command = ["add_domain", "--domain", "foobar."]
        out = self.badrequesttest(command)
        self.matchoutput(out, "'foobar.' is not a valid git branch name.",
                         command)

    def test_300_track_tracker(self):
        command = ["add_domain", "--domain=doubletracker", "--track=ut-prod"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Cannot nest tracking.  Try tracking "
                         "domain prod directly.", command)

    def test_900_verifyall(self):
        command = ["show_domain", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, "Domain: prod", command)
        self.matchoutput(out, "Domain: ut-prod", command)
        self.matchoutput(out, "Domain: unittest", command)
        self.matchoutput(out, "Domain: deployable", command)
        self.matchclean(out, "Sandbox: utsandbox", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddDomain)
    unittest.TextTestRunner(verbosity=2).run(suite)
