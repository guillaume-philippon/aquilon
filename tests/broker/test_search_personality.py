#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2013,2014,2015,2016  Contributor
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
"""Module for testing the search personality command."""

from collections import defaultdict

import unittest

if __name__ == "__main__":
    from broker import utils
    utils.import_depends()

from broker.brokertest import TestBrokerCommand
from broker.grntest import VerifyGrnsMixin


class TestSearchPersonality(VerifyGrnsMixin, TestBrokerCommand):
    def test_100_by_grn(self):
        command = ["search", "personality", "--grn", "grn:/ms/ei/aquilon/aqd"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utpers-dev@current", command)
        self.matchoutput(out, "aquilon/utunused/dev", command)
        self.matchoutput(out, "esx_cluster/esx_server", command)
        self.matchoutput(out, "esx_cluster/vulcan-10g-server-prod", command)

    def test_100_by_environment(self):
        command = ["search", "personality", "--host_environment", "prod"]
        out = self.commandtest(command)
        self.matchoutput(out, "aurora/generic", command)
        self.matchoutput(out, "filer/generic", command)
        self.matchoutput(out, "f5/generic", command)
        self.matchoutput(out, "esx_cluster/vulcan-10g-server-prod", command)
        self.matchoutput(out, "storagecluster/metrocluster", command)
        self.matchclean(out, "utunused/dev", command)

    def test_100_config_override(self):
        command = ["search", "personality", "--config_override"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utunused/dev", command)
        self.matchclean(out, "aurora/generic", command)
        self.matchclean(out, "filer/generic", command)

    def test_100_by_grn_environment(self):
        command = ["search", "personality",
                   "--host_environment", "dev", "--grn", "grn:/ms/ei/aquilon/aqd"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utunused/dev", command)
        self.matchoutput(out, "aquilon/utpers-dev@current", command)
        self.matchclean(out, "vulcan-10g-server-prod", command)

    def test_100_by_eon_id(self):
        command = ["search", "personality", "--eon_id", 2]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utpers-dev@current", command)
        self.matchoutput(out, "aquilon/utunused/dev", command)
        self.matchoutput(out, "esx_cluster/esx_server", command)
        self.matchoutput(out, "esx_cluster/vulcan-10g-server-prod", command)
        self.matchoutput(out, "gridcluster/hadoop", command)
        self.matchclean(out, "storagecluster/metrocluster", command)

    def test_100_by_dev_eon_id(self):
        command = ["search", "personality", "--host_environment", "dev", "--eon_id", 2]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utunused/dev", command)
        self.matchoutput(out, "aquilon/utpers-dev@current", command)
        self.matchclean(out, "vulcan-10g-server-prod", command)

    def test_100_fullinfo(self):
        command = ["search", "personality", "--host_environment", "dev",
                   "--eon_id", 2, "--fullinfo"]
        out = self.commandtest(command)
        self.matchoutput(out, "Personality: utunused/dev Archetype: aquilon",
                         command)
        self.matchoutput(out, "Config override: enabled", command)
        self.matchoutput(out, "Environment: dev", command)
        self.matchoutput(out, "Stage:", command)
        self.matchoutput(out, "Owned by GRN: %s" % self.eon_ids[2], command)
        self.matchoutput(out, "Used by GRN: %s" % self.eon_ids[2], command)
        self.matchclean(out, "inventory", command)

    def test_100_proto(self):
        command = ["search_personality", "--host_environment", "dev",
                   "--personality_stage", "current",
                   "--eon_id", 2, "--format=proto"]
        personalities = self.protobuftest(command, expect=14)
        pers_by_name_ver = defaultdict(dict)
        for p in personalities:
            pers_by_name_ver[p.name][p.stage] = p

        personality = pers_by_name_ver["badpersonality"].values()[0]
        self.assertEqual(personality.archetype.name, "aquilon")
        self.assertEqual(personality.name, "badpersonality")
        self.assertEqual(personality.stage, "")
        self.assertEqual(personality.owner_eonid, 2)
        self.assertEqual(personality.host_environment, "dev")

        personality = pers_by_name_ver["utpers-dev"]["current"]
        self.assertEqual(personality.archetype.name, "aquilon")
        self.assertEqual(personality.name, "utpers-dev")
        self.assertEqual(personality.stage, "current")
        self.assertEqual(personality.owner_eonid, 2)
        self.assertEqual(personality.host_environment, "dev")

    def test_100_non_unique_name(self):
        command = ["search", "personality", "--personality", "vulcan-10g-server-prod"]
        out = self.commandtest(command)
        self.matchoutput(out, "esx_cluster/vulcan-10g-server-prod", command)
        self.matchoutput(out, "vmhost/vulcan-10g-server-prod", command)

    def test_100_by_name_arch(self):
        command = ["search", "personality", "--personality", "vulcan-10g-server-prod",
                   "--archetype", "vmhost"]
        out = self.commandtest(command)
        self.matchoutput(out, "vmhost/vulcan-10g-server-prod", command)
        self.matchclean(out, "esx_cluster/vulcan-10g-server-prod", command)

    def test_100_by_required_service(self):
        command = ["search_personality", "--required_service", "chooser2"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/unixeng-test@current", command)
        self.matchclean(out, "compileserver", command)

    def test_used(self):
        command = ["search_personality", "--used"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/compileserver", command)
        self.matchoutput(out, "aquilon/unixeng-test@current", command)
        self.matchoutput(out, "aurora/generic", command)
        self.matchoutput(out, "esx_cluster/vulcan2-server-dev", command)

    def test_unused(self):
        command = ["search_personality", "--unused"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/badpersonality", command)
        self.matchoutput(out, "aquilon/nostage@next", command)
        self.matchoutput(out, "aquilon/utunused/dev", command)
        self.matchoutput(out, "esx_cluster/nostage@next", command)
        self.matchoutput(out, "vmhost/nostage@next", command)

    def test_110_show_diff_1(self):
        command = ["show_diff", "--personality=utunused/dev",
                   "--archetype=aquilon", "--other=inventory"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'missing Options in Personality aquilon/inventory:\s+ConfigOverride',
                          command)
        self.searchoutput(out,
                          r'missing Grns in Personality aquilon/inventory:\s+'
                          r'esp: grn:/ms/ei/aquilon/aqd',
                          command)

    def test_110_show_diff_2(self):
        command = ["show_diff", "--personality=utunused/dev",
                   "--archetype=aquilon", "--other=vulcan-10g-server-prod", "--other_archetype=vmhost"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'missing Options in Personality aquilon/utunused/dev:\s+Cluster Required',
                          command)
        self.searchoutput(out,
                          r'matching Options with different values:\s+Environment value=dev, othervalue=prod',
                          command)

    def test_200_no_match(self):
        command = ["search", "personality", "--archetype", "aurora",
                   "--host_environment", "prod", "--eon_id", 2]
        self.noouttest(command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchPersonality)
    unittest.TextTestRunner(verbosity=2).run(suite)
