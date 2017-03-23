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
"""Module for testing the manage command."""

import os

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from broker.brokertest import TestBrokerCommand


class TestManageValidateBranch(TestBrokerCommand):

    def test_000_add_managetest1_sandbox(self):
        self.successtest(["add", "sandbox", "--sandbox", "managetest1"])

    def test_000_add_managetest2_sandbox(self):
        self.successtest(["add", "sandbox", "--sandbox", "managetest2"])

    def test_100_manage_for_uncommitted_change(self):
        # aquilon63.aqd-unittest.ms.com & aquilon64.aqd-unittest.ms.com are
        # sitting in "%s/utsandbox" we manage it to managetest1 to start clean.
        self.successtest(["manage", "--hostname=aquilon63.aqd-unittest.ms.com",
                          "--sandbox=%s/managetest1" % self.user, "--force"])
        self.successtest(["manage", "--hostname=aquilon64.aqd-unittest.ms.com",
                          "--sandbox=%s/managetest1" % self.user, "--force"])

    def test_101_make_uncommitted_change(self):
        sandboxdir = os.path.join(self.sandboxdir, "managetest1")
        template = self.find_template("aquilon", "archetype", "base",
                                      sandbox="managetest1")
        with open(template) as f:
            contents = f.readlines()
        contents.append("#Added by test_manage unittest %s \n" % sandboxdir)

        with open(template, 'w') as f:
            f.writelines(contents)

        self.gitcommand(["add", template], cwd=sandboxdir)

    def test_102_fail_uncommitted_change(self):
        command = ["manage", "--hostname", "aquilon63.aqd-unittest.ms.com",
                   "--sandbox", "%s/managetest2" % self.user]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "The source sandbox managetest1 contains uncommitted"
                         " files.",
                         command)

    def test_110_commit_uncommitted_change(self):
        sandboxdir = os.path.join(self.sandboxdir, "managetest1")
        self.gitcommand(["commit", "-a", "-m",
                         "added test_manage unittest comment"], cwd=sandboxdir)

    def test_112_fail_missing_committed_change_in_template_king(self):
        command = ["manage", "--hostname", "aquilon63.aqd-unittest.ms.com",
                   "--sandbox", "%s/managetest2" % self.user]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "The latest commit of sandbox managetest1 has "
                         "not been published to template-king yet.",
                         command)

    def test_114_publish_committed_change(self):
        sandboxdir = os.path.join(self.sandboxdir, "managetest1")
        self.successtest(["publish", "--branch", "managetest1"],
                         env=self.gitenv(), cwd=sandboxdir)

    def test_115_fail_missing_committed_change_in_target(self):
        command = ["manage", "--hostname", "aquilon63.aqd-unittest.ms.com",
                   "--sandbox", "%s/managetest2" % self.user]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "The target sandbox managetest2 does not contain the "
                         "latest commit from source sandbox managetest1.",
                         command)

    def test_116_pull_committed_change(self):
        kingdir = self.config.get("broker", "kingdir")
        managetest2dir = os.path.join(self.sandboxdir, "managetest2")
        self.gitcommand(["pull", "--no-ff", kingdir, "managetest1"],
                        cwd=managetest2dir)

    def test_120_manage_committed(self):
        self.successtest(["manage", "--hostname=aquilon63.aqd-unittest.ms.com",
                          "--sandbox=%s/managetest2" % self.user])

    def test_121_verify_manage_committed(self):
        command = "show host --hostname aquilon63.aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Primary Name: aquilon63.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "Sandbox: %s/managetest2" % self.user, command)

    def test_130_force_manage_committed(self):
        self.successtest(["manage", "--hostname=aquilon64.aqd-unittest.ms.com",
                          "--sandbox=%s/managetest2" % self.user, "--force"])

    def test_131_verify_force_manage_committed(self):
        command = "show host --hostname aquilon64.aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Primary Name: aquilon64.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "Sandbox: %s/managetest2" % self.user, command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestManageValidateBranch)
    unittest.TextTestRunner(verbosity=2).run(suite)
