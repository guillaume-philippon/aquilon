#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017  Contributor
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
"""Module for testing the deploy domain command."""

import os.path
from shutil import rmtree

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDeployDomain(TestBrokerCommand):

    def head_commit(self, sandbox, ref="HEAD"):
        sandboxdir = os.path.join(self.sandboxdir, sandbox)
        head, _ = self.gitcommand(["rev-parse", "%s^{commit}" % ref],
                                  cwd=sandboxdir)
        head = head.strip()
        return head

    def test_100_deploychangetest1domain(self):
        command = ["deploy", "--source", "changetest1",
                   "--target", "deployable", "--reason", "Test reason"]
        out = self.statustest(command)
        self.matchoutput(out, "Updating the checked out copy of domain "
                         "deployable...", command)

    def test_110_verifydeploy(self):
        template = self.find_template("aquilon", "archetype", "base",
                                      domain="deployable")
        with open(template) as f:
            contents = f.readlines()
        self.assertEqual(contents[-1], "#Added by unittest\n")

    def test_110_verifydeploylog(self):
        kingdir = self.config.get("broker", "kingdir")
        command = ["show", "--no-patch", "--pretty=full", "deployable"]
        out, _ = self.gitcommand(command, cwd=kingdir)
        self.matchoutput(out, "User:", command)
        self.matchoutput(out, "Request-ID:", command)
        self.matchoutput(out, "Reason: Test reason", command)
        self.matchclean(out, "Justification:", command)
        self.matchclean(out, "Code-Review-URL", command)
        self.matchclean(out, "Testing-URL", command)

        author_email = self.config.get("broker", "git_author_email")
        self.matchoutput(out, "Author: %s <%s>" % (self.user, author_email),
                         command)

    def test_120_deployfail(self):
        command = ["deploy", "--source", "changetest1",
                   "--target", "prod"]
        _, err = self.failuretest(command, 4)
        self.matchoutput(err,
                         "Domain prod is under change management control.  "
                         "Please specify --justification.",
                         command)

    def test_120_deploydryrun(self):
        kingdir = self.config.get("broker", "kingdir")
        old_prod, _ = self.gitcommand(["rev-list", "--max-count=1", "prod"],
                                      cwd=kingdir)

        command = ["deploy", "--source", "changetest1",
                   "--target", "prod", "--dryrun"]
        self.successtest(command)

        new_prod, _ = self.gitcommand(["rev-list", "--max-count=1", "prod"],
                                      cwd=kingdir)
        self.assertEqual(old_prod, new_prod,
                         "Domain prod changed despite --dryrun")

    def test_120_deploybadjustification(self):
        command = ["deploy", "--source", "changetest1", "--target", "prod",
                   "--justification", "I felt like deploying changes."]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Failed to parse the justification", command)

    def test_123_request_review(self):
        command = ["request_review", "--source", "changetest1", "--target", "prod"]
        self.noouttest(command)

    def test_123_request_review_tracking(self):
        command = ["request_review", "--source", "changetest1", "--target", "ut-prod"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "The target needs to be a non-tracking domain, "
                         "maybe you meant prod?", command)

    def test_124_show_review(self):
        changetest1_head = self.head_commit("changetest1")
        command = ["show_review", "--source", "changetest1", "--target", "prod"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Review request
              Target Domain: prod
              Source Sandbox: changetest1
                Published Commit: %s
              Testing Status: Untested
              Approval Status: No decision
            """ % changetest1_head,
                           command)

    def test_124_show_review_all(self):
        changetest1_head = self.head_commit("changetest1")
        command = ["show_review", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, changetest1_head, command)

    def test_125_update_review_cr(self):
        command = ["update_review", "--source", "changetest1", "--target", "prod",
                   "--review_url", "http://review.example.org/changes/1234"]
        self.noouttest(command)

    def test_126_update_review_testing(self):
        changetest1_head = self.head_commit("changetest1")
        prod_head = self.head_commit("changetest1", ref="origin/prod")
        command = ["update_review", "--source", "changetest1", "--target", "prod",
                   "--commit_id", changetest1_head,
                   "--target_commit_tested", prod_head,
                   "--testing_url", "http://ci.example.org/builds/5678",
                   "--testing_succeeded"]
        self.noouttest(command)

    def test_126_update_review_approval(self):
        changetest1_head = self.head_commit("changetest1")
        command = ["update_review", "--source", "changetest1", "--target", "prod",
                   "--commit_id", changetest1_head,
                   "--approved"]
        self.noouttest(command)

    def test_128_show_review(self):
        changetest1_head = self.head_commit("changetest1")
        prod_head = self.head_commit("changetest1", ref="origin/prod")
        command = ["show_review", "--source", "changetest1", "--target", "prod"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Review request
              Target Domain: prod
                Tested Commit: %s
              Source Sandbox: changetest1
                Published Commit: %s
              Code Review URL: http://review.example.org/changes/1234
              Testing URL: http://ci.example.org/builds/5678
              Testing Status: Success
              Approval Status: Approved
            """ % (prod_head, changetest1_head),
                           command)

    def test_128_show_review_csv(self):
        changetest1_head = self.head_commit("changetest1")
        prod_head = self.head_commit("changetest1", ref="origin/prod")
        command = ["show_review", "--source", "changetest1", "--target", "prod",
                   "--format", "csv"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         "prod,changetest1,%s,http://review.example.org/changes/1234,http://ci.example.org/builds/5678,%s,True,True"
                         % (changetest1_head, prod_head),
                         command)

    def test_129_bad_target_commit_id(self):
        changetest1_head = self.head_commit("changetest1")
        commit_not_in_templates = "576afd9bd9f620293a9e0e249032be5157ba5d29"
        command = ["update_review", "--source", "changetest1", "--target", "prod",
                   "--commit_id", changetest1_head, "--testing_failed",
                   "--target_commit_tested", commit_not_in_templates]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Domain prod does not contain commit %s." %
                         commit_not_in_templates, command)

    def test_129_stale_testing(self):
        changetest1_head = self.head_commit("changetest1")
        commit_not_in_templates = "576afd9bd9f620293a9e0e249032be5157ba5d29"
        command = ["update_review", "--source", "changetest1", "--target", "prod",
                   "--commit_id", commit_not_in_templates,
                   "--testing_url", "http://ci.example.org/builds/5677",
                   "--testing_failed"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Possible attempt to update an old review record - "
                         "the commit being reviewed is %s, not %s." %
                         (changetest1_head, commit_not_in_templates),
                         command)

    def test_129_short_commit(self):
        abbrev_hash_not_in_templates = "576afd9bd9f620"
        command = ["update_review", "--source", "changetest1", "--target", "prod",
                   "--commit_id", abbrev_hash_not_in_templates,
                   "--testing_url", "http://ci.example.org/builds/5677",
                   "--testing_failed"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Invalid commit ID (%s), make sure to pass the "
                         "full hash." % abbrev_hash_not_in_templates, command)

    def test_130_deploynosync(self):
        command = ["deploy", "--source", "changetest1", "--target", "prod",
                   "--nosync", "--justification", "tcm=12345678",
                   "--reason", "Just because"]
        out = self.statustest(command)
        self.matchoutput(out, "Updating the checked out copy of domain prod...",
                         command)
        self.matchclean(out, "ut-prod", command)
        self.matchclean(out, "not approved", command)

    def test_131_verifydeploylog(self):
        kingdir = self.config.get("broker", "kingdir")
        command = ["show", "--no-patch", "--format=%B", "prod"]
        out, _ = self.gitcommand(command, cwd=kingdir)
        self.matchoutput(out, "User:", command)
        self.matchoutput(out, "Request-ID:", command)
        self.matchoutput(out, "Justification: tcm=12345678", command)
        self.matchoutput(out, "Reason: Just because", command)
        self.matchoutput(out,
                         "Code-Review-URL: http://review.example.org/changes/1234",
                         command)
        self.matchoutput(out,
                         "Testing-URL: http://ci.example.org/builds/5678",
                         command)

    def test_200_verifynosync(self):
        # The change should be in prod...
        template = self.find_template("aquilon", "archetype", "base",
                                      domain="prod")
        with open(template) as f:
            contents = f.readlines()
        self.assertEqual(contents[-1], "#Added by unittest\n")
        # ...but not in the ut-prod tracking domain.
        template = self.find_template("aquilon", "archetype", "base",
                                      domain="ut-prod")
        with open(template) as f:
            contents = f.readlines()
        self.assertNotEqual(contents[-1], "#Added by unittest\n")

    def test_210_verifynosynclog(self):
        kingdir = self.config.get("broker", "kingdir")

        # Note: "prod" is a copy of the real thing so limit the amount of
        # history checked to avoid being fooled by real commits

        # The change must be in prod...
        command = ["show", "--no-patch", "--format=%B", "prod"]
        out, _ = self.gitcommand(command, cwd=kingdir)
        self.matchoutput(out, "Justification: tcm=12345678", command)
        self.matchoutput(out, "Reason: Just because", command)

        # ... but not in ut-prod
        command = ["show", "--no-patch", "--format=%B", "ut-prod"]
        out, _ = self.gitcommand(command, cwd=kingdir)
        self.matchclean(out, "tcm=12345678", command)

    def test_300_add_advanced(self):
        self.successtest(["add", "sandbox", "--sandbox", "advanced",
                          "--start", "prod"])

    def test_310_deploy_leftbehind(self):
        command = ["deploy", "--source", "advanced", "--target", "leftbehind"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "You're trying to deploy a sandbox to a domain that "
                         "does not contain the commit where the sandbox was "
                         "branched from.",
                         command)

    def test_310_review_leftbehild(self):
        command = ["request_review", "--source", "advanced", "--target", "leftbehind"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Domain leftbehind does not contain the commit where "
                         "sandbox advanced was branched from.",
                         command)

    def test_320_update_leftbehind(self):
        command = ["deploy", "--source", "prod", "--target", "leftbehind"]
        self.successtest(command)

    def test_330_deploy_again(self):
        command = ["deploy", "--source", "advanced", "--target", "leftbehind"]
        self.successtest(command)

    def test_340_cleanup_advanced(self):
        self.successtest(["del_sandbox", "--sandbox", "advanced"])
        sandboxdir = os.path.join(self.sandboxdir, "advanced")
        rmtree(sandboxdir, ignore_errors=True)

    def test_800_deploy_utsandbox(self):
        # utsandbox contains changes needed to compile test hosts
        command = ["deploy", "--source", "utsandbox", "--target", "prod",
                   "--justification", "tcm=12345678"]
        out = self.statustest(command)
        for domain in ["prod", "ut-prod", "netinfra"]:
            self.matchoutput(out,
                             "Updating the checked out copy of domain %s..." %
                             domain, command)
        #self.matchoutput(out, "Warning: this deployment request was "
        #                 "not approved", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDeployDomain)
    unittest.TextTestRunner(verbosity=2).run(suite)
