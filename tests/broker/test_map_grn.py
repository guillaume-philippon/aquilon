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
"""Module for testing GRN mapping."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from broker.brokertest import TestBrokerCommand
from broker.grntest import VerifyGrnsMixin
from broker.personalitytest import PersonalityTestMixin

GRN = "grn:/ms/ei/aquilon/unittest"


class TestMapGrn(VerifyGrnsMixin, PersonalityTestMixin, TestBrokerCommand):

    grn_list = ["grn:/ms/ei/aquilon/aqd", "grn:/ms/ei/aquilon/unittest"]
    grn_maps = {"esp": grn_list, "atarget": ["grn:/example/cards"]}

    def test_100_map_bad_personality(self):
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--personality", "compileserver", "--target", "badtarget"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Invalid target badtarget for archetype aquilon, "
                         "please choose from: esp, hlmplus, atarget.", command)

    def test_105_map_personality(self):
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--personality", "compileserver", "--target", "esp"]
        self.successtest(command)

        command = ["map", "grn", "--grn", "grn:/example/cards",
                   "--personality", "compileserver", "--target", "atarget"]
        self.successtest(command)

    def test_110_verify_personality(self):
        command = ["show", "personality", "--personality", "compileserver"]
        out = self.commandtest(command)
        self.matchoutput(out, "GRN: grn:/ms/ei/aquilon/aqd [target: esp]", command)

        command = ["cat", "--archetype=aquilon", "--personality=compileserver"]
        out = self.commandtest(command)
        self.check_personality_grns(out, "grn:/ms/ei/aquilon/unittest",
                                    self.grn_maps, command)

        command = ["show_personality", "--archetype=aquilon",
                   "--personality=compileserver", "--format=proto"]
        personality = self.protobuftest(command, expect=1)[0]
        self.assertEqual(personality.archetype.name, "aquilon")
        self.assertEqual(personality.name, "compileserver")
        self.assertEqual(personality.owner_eonid,
                         self.grns["grn:/ms/ei/aquilon/unittest"])
        grns = set((rec.target, rec.eonid) for rec in personality.eonid_maps)
        self.assertEqual(grns, set([('atarget', 6), ('esp', 2), ('esp', 3)]))

    def test_115_verify_diff(self):
        command = ["show_diff", "--archetype", "aquilon",
                   "--personality", "compileserver", "--other", "inventory"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'Differences for Grns:\s*'
                          r'missing Grns in Personality aquilon/inventory:\s*'
                          r'atarget: grn:/example/cards\s*'
                          r'esp: grn:/ms/ei/aquilon/aqd\s*',
                          command)

    def test_120_verify_host(self):
        command = ["show_host", "--hostname", "unittest20.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "GRN: grn:/ms/ei/aquilon/aqd [target: esp]", command)

    def test_130_map_host(self):
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--hostname", "unittest12.aqd-unittest.ms.com",
                   "--target", "esp"]
        self.statustest(command)

    def test_131_map_host_again(self):
        scratchfile = self.writescratch("hostlist",
                                        "unittest12.aqd-unittest.ms.com")
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--list", scratchfile, "--target", "esp"]
        # TODO: should this throw an error?
        self.statustest(command)

    def test_132_map_host_plus_pers(self):
        # The personality already includes the GRN
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--hostname", "unittest00.one-nyp.ms.com", "--target", "esp"]
        self.noouttest(command)

        command = ["map", "grn", "--grn", "grn:/example/cards",
                   "--hostname", "unittest00.one-nyp.ms.com", "--target", "atarget"]
        self.noouttest(command)

    def test_135_show_unitesst00_grns(self):
        ip = self.net["unknown0"].usable[2]
        command = ["show_host", "--hostname", "unittest00.one-nyp.ms.com",
                   "--grns"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Primary Name: unittest00.one-nyp.ms.com [%s]
              Owned by GRN: grn:/ms/ei/aquilon/unittest [inherited]
              Used by GRN: grn:/example/cards [target: atarget]
              Used by GRN: grn:/ms/ei/aquilon/aqd [target: esp]
              Used by GRN: grn:/ms/ei/aquilon/unittest [target: esp, inherited]
            """ % ip, command)

    def test_140_search(self):
        command = ["search", "host", "--grn", "grn:/ms/ei/aquilon/aqd"]
        out = self.commandtest(command)
        self.matchoutput(out, "unittest00.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest20.aqd-unittest.ms.com", command)
        self.matchoutput(out, "unittest12.aqd-unittest.ms.com", command)

    def test_150_map_disabled(self):
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon",
                   "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--target", "esp"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "GRN grn:/ms/ei/aquilon is not usable for new "
                         "systems.", command)

    def test_151_enable_grn(self):
        self.noouttest(["update_grn", "--grn", "grn:/ms/ei/aquilon",
                        "--nodisabled"])
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon",
                   "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--target", "esp"]
        self.noouttest(command)

    def test_152_disable_again(self):
        self.noouttest(["update_grn", "--grn", "grn:/ms/ei/aquilon",
                        "--disabled"])

    def test_153_unmap_disabled(self):
        command = ["unmap", "grn", "--grn", "grn:/ms/ei/aquilon",
                   "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--target", "esp"]
        self.noouttest(command)

    def test_160_map_missing_eonid(self):
        command = ["map", "grn", "--eon_id", "987654321", "--target", "esp",
                   "--hostname", "unittest20.aqd-unittest.ms.com"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "EON ID 987654321 not found.", command)

    def test_160_map_missing_grn(self):
        command = ["map", "grn", "--grn", "grn:/ms/no-such-grn",
                   "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--target", "esp"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "GRN grn:/ms/no-such-grn not found.", command)

    def test_200_verify_unittest00(self):
        command = ["cat", "--hostname", "unittest00.one-nyp.ms.com", "--data",
                   "--generate"]
        out = self.commandtest(command)
        # The GRN is mapped to both the host and the personality; verify it is
        # not duplicated. Should print out both the host mapped
        # personality mapped grns
        self.check_grns(out, {"esp": [self.grn_list[0]]}, command)

    def test_210_verify_unittest20(self):
        command = ["cat", "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--data", "--generate"]
        out = self.commandtest(command)
        # The GRN is mapped to the personality only
        self.matchclean(out, "eon_id_maps", command)

    def test_220_verify_unittest12(self):
        command = ["cat", "--hostname", "unittest12.aqd-unittest.ms.com",
                   "--data", "--generate"]
        out = self.commandtest(command)
        # The GRN is mapped to the host only
        self.check_grns(out, {"esp": [self.grn_list[0]]}, command)

    def test_300_delete_used_byhost(self):
        command = ["del", "grn", "--grn", "grn:/ms/ei/aquilon/aqd"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "GRN grn:/ms/ei/aquilon/aqd is still used by "
                         "hosts, and cannot be deleted.", command)

    def test_310_delete_missing(self):
        command = ["del", "grn", "--eon_id", "987654321"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "EON ID 987654321 not found.", command)

    def test_320_unmap_unittest12(self):
        command = ["unmap", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--hostname", "unittest12.aqd-unittest.ms.com",
                   "--target", "esp"]
        self.statustest(command)

    def test_320_unmap_unittest00(self):
        command = ["unmap", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--hostname", "unittest00.one-nyp.ms.com", "--target", "esp"]
        self.noouttest(command)

    def test_321_verify_unittest12(self):
        command = ["show_host", "--hostname", "unittest12.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        # Make sure not to match the personality GRN
        self.searchclean(out, r"^  GRN", command)

    def test_322_verify_search(self):
        command = ["search", "host", "--grn", "grn:/ms/ei/aquilon/aqd"]
        out = self.commandtest(command)
        # unittest00 is still included due to its personality
        self.matchoutput(out, "unittest00.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest20.aqd-unittest.ms.com", command)
        self.matchclean(out, "unittest12.aqd-unittest.ms.com", command)

    def test_325_unmap_host_again(self):
        scratchfile = self.writescratch("hostlist",
                                        "unittest12.aqd-unittest.ms.com")
        command = ["unmap", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--list", scratchfile, "--target", "esp"]
        # TODO: should this throw an error?
        self.statustest(command)

    def test_330_delete_used_bypers(self):
        command = ["del", "grn", "--grn", "grn:/ms/windows/desktop"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "GRN grn:/ms/windows/desktop is still used "
                         "by personalities, and cannot be deleted.", command)

    def test_340_unmap_personality(self):
        command = ["unmap", "grn", "--grn", "grn:/example/cards",
                   "--personality", "compileserver", "--target", "atarget"]
        self.noouttest(command)

        command = ["cat", "--archetype", "aquilon",
                   "--personality", "compileserver"]
        out = self.commandtest(command)

        grn_list = ["grn:/ms/ei/aquilon/aqd", "grn:/ms/ei/aquilon/unittest"]
        self.check_personality_grns(out, "grn:/ms/ei/aquilon/unittest",
                                    {"esp": grn_list}, command)

        command = ["unmap", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--personality", "compileserver", "--target", "esp"]
        self.noouttest(command)

    def test_400_verify_unittest00(self):
        command = ["cat", "--hostname", "unittest00.one-nyp.ms.com", "--data",
                   "--generate"]
        out = self.commandtest(command)
        self.matchclean(out, "eon_id_maps/esp", command)

    def test_410_verify_unittest20(self):
        command = ["cat", "--hostname", "unittest20.aqd-unittest.ms.com",
                   "--data", "--generate"]
        out = self.commandtest(command)
        # The GRN was mapped to the personality only
        self.matchclean(out, "eon_id_maps", command)

    def test_420_verify_unittest12(self):
        command = ["cat", "--hostname", "unittest12.aqd-unittest.ms.com",
                   "--data", "--generate"]
        out = self.commandtest(command)
        # The GRN was mapped to the host only
        self.matchclean(out, "eon_id_maps", command)

    def test_500_fail_map_overlimitlist(self):
        hostlimit = self.config.getint("broker", "map_grn_max_list_size")
        hosts = []
        for i in range(1, 20):
            hosts.append("thishostdoesnotexist%d.aqd-unittest.ms.com" % i)
        scratchfile = self.writescratch("mapgrnlistlimit", "\n".join(hosts))
        command = ["map", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--list", scratchfile, "--target", "esp"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "The number of hosts in list {0:d} can not be more "
                         "than {1:d}".format(len(hosts), hostlimit),
                         command)

    def test_500_fail_unmap_overlimitlist(self):
        hostlimit = self.config.getint("broker", "unmap_grn_max_list_size")
        hosts = []
        for i in range(1, 20):
            hosts.append("thishostdoesnotexist%d.aqd-unittest.ms.com" % i)
        scratchfile = self.writescratch("mapgrnlistlimit", "\n".join(hosts))
        command = ["unmap", "grn", "--grn", "grn:/ms/ei/aquilon/aqd",
                   "--list", scratchfile, "--target", "esp"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "The number of hosts in list {0:d} can not be more "
                         "than {1:d}".format(len(hosts), hostlimit),
                         command)

    def test_500_no_target_configured(self):
        command = ["map_grn", "--grn", "grn:/ms/ei/aquilon/unittest",
                   "--target", "esp",
                   "--hostname", "%s.ms.com" % self.aurora_with_node]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Archetype aurora has no valid GRN targets "
                         "configured.", command)

    def test_500_missing_personality(self):
        command = ["map_grn", "--grn", "grn:/ms/ei/aquilon/unittest",
                   "--target", "esp", "--archetype", "aquilon",
                   "--personality", "personality-does-not-exist"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Personality personality-does-not-exist, "
                         "archetype aquilon not found.",
                         command)

    def test_500_missing_personality_stage(self):
        command = ["map_grn", "--grn", "grn:/ms/ei/aquilon/unittest",
                   "--target", "esp", "--archetype", "aquilon",
                   "--personality", "nostage",
                   "--personality_stage", "previous"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Personality aquilon/nostage does not have stage "
                         "previous.",
                         command)

    def test_500_bad_personality_stage(self):
        command = ["map_grn", "--grn", "grn:/ms/ei/aquilon/unittest",
                   "--target", "esp", "--archetype", "aquilon",
                   "--personality", "nostage",
                   "--personality_stage", "no-such-stage"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "'no-such-stage' is not a valid personality "
                         "stage.", command)

    def test_600_unmap_personality(self):
        for grn in self.grn_list:
            command = ["map", "grn", "--grn", grn,
                       "--personality", "compileserver", "--target", "esp"]
            self.successtest(command)

        command = ["cat", "--archetype", "aquilon", "--personality", "compileserver"]
        out = self.commandtest(command)
        self.check_personality_grns(out, "grn:/ms/ei/aquilon/unittest",
                                    {"esp": self.grn_list}, command)

        command = ["unmap", "grn", "--clearall",
                   "--personality", "compileserver", "--target", "esp"]
        self.successtest(command)

        command = ["cat", "--archetype", "aquilon", "--personality", "compileserver"]
        out = self.commandtest(command)
        self.searchclean(out, "system/eon_id_maps", command)

    def test_620_unmap_unittest12(self):
        for grn in self.grn_list:
            command = ["map", "grn", "--grn", grn,
                       "--hostname", "unittest12.aqd-unittest.ms.com", "--target", "esp"]
            self.statustest(command)

        command = ["show_host", "--hostname", "unittest12.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/unittest [target: esp]", command)
        self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/aqd [target: esp]", command)

        command = ["unmap", "grn", "--clearall",
                   "--hostname", "unittest12.aqd-unittest.ms.com",
                   "--target", "esp"]
        self.successtest(command)

        command = ["show_host", "--hostname", "unittest12.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchclean(out, "^  Used by GRN", command)

    def test_630_map_host_list(self):
        scratchfile = self.writescratch("hostlist",
                                        "unittest12.aqd-unittest.ms.com")
        for grn in self.grn_list:
            command = ["map", "grn", "--grn", grn, "--list", scratchfile,
                       "--target", "esp"]
            self.statustest(command)

        command = ["show_host", "--hostname", "unittest12.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/unittest [target: esp]", command)
        self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/aqd [target: esp]", command)

        command = ["unmap", "grn", "--clearall", "--list", scratchfile,
                   "--target", "esp"]
        self.successtest(command)

        command = ["show_host", "--hostname", "unittest12.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchclean(out, "^  Used by GRN", command)

    def test_700_map_cluster(self):
        cluster = "utecl11"
        for grn in self.grn_list:
            command = ["map", "grn", "--grn", grn, "--membersof", cluster,
                       "--target", "esp"]
            self.statustest(command)

        command = ["search_host", "--cluster", cluster]
        hosts = sorted(self.commandtest(command).splitlines())

        for host in hosts:
            command = ["show_host", "--hostname", host, "--grns"]
            out = self.commandtest(command)
            self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/unittest [target: esp]", command)
            self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/aqd [target: esp]", command)

    def test_701_unmap_cluster(self):
        cluster = "utecl11"
        command = ["unmap", "grn", "--grn", self.grn_list[0], "--membersof", cluster,
                   "--target", "esp"]
        self.statustest(command)

        command = ["search_host", "--cluster", cluster]
        hosts = sorted(self.commandtest(command).splitlines())

        for host in hosts:
            command = ["show_host", "--hostname", host, "--grns"]
            out = self.commandtest(command)
            self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/unittest [target: esp]", command)
            self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/aqd [target: esp, inherited]", command)

        command = ["unmap", "grn", "--clearall", "--membersof", cluster, "--target", "esp"]
        self.statustest(command)
        for host in hosts:
            command = ["show_host", "--hostname", host, "--grns"]
            out = self.commandtest(command)
            self.matchoutput(out, "Used by GRN: grn:/ms/ei/aquilon/aqd [target: esp, inherited]", command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMapGrn)
    unittest.TextTestRunner(verbosity=2).run(suite)
