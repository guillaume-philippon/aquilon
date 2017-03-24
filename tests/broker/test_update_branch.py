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
"""Module for testing the update domain command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestUpdateBranch(TestBrokerCommand):
    # FIXME: Add some tests around (no)autosync
    # FIXME: Verify against sandboxes

    def test_100_update_deployable(self):
        self.noouttest(["update", "domain", "--domain", "deployable",
                        "--comments", "New domain comments",
                        "--compiler_version=utpanc"])

    def test_105_verify_deployable(self):
        command = "show domain --domain deployable"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Domain: deployable", command)
        self.searchoutput(out, r"Compiler: .*/panc-utpanc.jar", command)
        self.matchoutput(out, "Comments: New domain comments", command)

    def test_110_update_prod(self):
        self.noouttest(["update", "domain", "--domain", "prod",
                        "--change_manager"])

    def test_115_verify_prod(self):
        command = ["show", "domain", "--domain", "prod"]
        out = self.commandtest(command)
        self.matchoutput(out, "Requires Change Manager: True", command)

    def test_120_update_unittest(self):
        self.noouttest(["update", "domain", "--domain", "unittest",
                        "--allow_manage"])

    def test_125_verify_unittest(self):
        command = ["show", "domain", "--domain", "unittest"]
        out = self.commandtest(command)
        self.matchoutput(out, "May Contain Hosts/Clusters: True", command)

    def test_130_update_nomanage(self):
        command = ["update", "domain", "--domain", "nomanage",
                   "--disallow_manage"]
        self.noouttest(command)

    def test_135_verify_nomanage(self):
        command = ["show", "domain", "--domain", "nomanage"]
        out = self.commandtest(command)
        self.matchoutput(out, "May Contain Hosts/Clusters: False", command)

    def test_140_archive(self):
        command = ["update_domain", "--domain", "deployable", "--archived"]
        self.noouttest(command)

    def test_141_verify_archive(self):
        command = ["show_domain", "--domain", "deployable"]
        out = self.commandtest(command)
        self.matchoutput(out, "Archived: True", command)
        self.matchoutput(out, "May Contain Hosts/Clusters: False", command)

    def test_142_manage_archived(self):
        command = ["update_domain", "--domain", "deployable", "--allow_manage"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Domain deployable is archived, cannot allow "
                         "managing hosts to it.", command)

    def test_148_unarchive(self):
        command = ["update_domain", "--domain", "deployable", "--noarchived",
                   "--allow_manage"]
        self.noouttest(command)

    def test_149_verify_unarchive(self):
        command = ["show_domain", "--domain", "deployable"]
        out = self.commandtest(command)
        self.matchoutput(out, "Archived: False", command)
        self.matchoutput(out, "May Contain Hosts/Clusters: True", command)

    def test_200_bad_compiler_version_characters(self):
        command = ["update_sandbox", "--sandbox=changetest1",
                   "--compiler_version=version!with@bad#characters"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Invalid characters in compiler version",
                         command)

    def test_200_bad_compiler_version(self):
        command = ["update_sandbox", "--sandbox=changetest1",
                   "--compiler_version=version-does-not-exist"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Compiler not found at", command)

    def test_200_not_a_domain(self):
        command = ["update_domain", "--domain=changetest1", "--change_manager"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Domain changetest1 not found.", command)

    def test_200_not_a_sandbox(self):
        command = ["update_sandbox", "--sandbox=unittest", "--autosync"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Sandbox unittest not found.", command)

    def test_200_change_manager_for_tracked(self):
        command = ["update_domain", "--domain=ut-prod", "--change_manager"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Cannot enforce a change manager for tracking "
                         "domains.",
                         command)

    def test_200_archive_tracking(self):
        command = ["update_domain", "--domain", "unittest", "--archived"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Domain unittest is a tracking domain and "
                         "cannot be archived.", command)

    def test_300_verify_search_chm(self):
        command = ["search", "domain", "--change_manager"]
        out = self.commandtest(command)
        self.matchoutput(out, "prod", command)
        self.matchclean(out, "ut-prod", command)
        self.matchclean(out, "deployable", command)

    def test_300_verify_search_version(self):
        command = ["search", "domain", "--compiler_version", "utpanc"]
        out = self.commandtest(command)
        self.matchclean(out, "prod", command)
        self.matchclean(out, "ut-prod", command)
        self.matchoutput(out, "deployable", command)

    def testupdateunittestxml(self):
        # Make this domain produce XML, regardless of the global default
        command = ["update_domain", "--domain", "unittest-xml",
                   "--profile_formats", "pan"]
        self.noouttest(command)

    def testverifyunittestxml(self):
        command = ["show_domain", "--domain", "unittest-xml"]
        out = self.commandtest(command)
        self.matchoutput(out, "Profile Formats: pan", command)

    def testupdateunittestjson(self):
        # Make this domain produce JSON, regardless of the global default
        command = ["update_domain", "--domain", "unittest-json",
                   "--profile_formats", "json"]
        self.noouttest(command)

    def testverifyunittestjson(self):
        command = ["show_domain", "--domain", "unittest-json"]
        out = self.commandtest(command)
        self.matchoutput(out, "Profile Formats: json", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUpdateBranch)
    unittest.TextTestRunner(verbosity=2).run(suite)
