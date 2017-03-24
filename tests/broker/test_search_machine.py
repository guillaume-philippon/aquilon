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
"""Module for testing the search machine command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestSearchMachine(TestBrokerCommand):

    def testclusteravailable(self):
        command = "search machine --cluster utecl1"
        out = self.commandtest(command.split(" "))
        for i in range(1, 9):
            self.matchoutput(out, "evm%s" % i, command)
        self.matchclean(out, "evm9", command)

    def testclusterunavailable(self):
        command = "search machine --cluster cluster-does-not-exist"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "Cluster cluster-does-not-exist not found.",
                         command)

    def testlocation(self):
        command = "search machine --building ut"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "evm", command)
        self.matchoutput(out, "ut", command)

    def testdesk(self):
        command = "search machine --desk utdesk1"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "utnorack", command)
        self.matchclean(out, "evm", command)

    def testlocationexact(self):
        # Should only show virtual machines, since all the physical machines
        # are at the rack level and this search is exact.
        command = "search machine --building ut --exact_location"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "evm", command)
        self.matchclean(out, "ut", command)

    def testcpucount(self):
        command = "search machine --cpucount 1"
        out = self.commandtest(command.split(" "))
        # Currently only virtual machines have 1 cpu in the tests...
        for i in range(1, 10):
            self.matchoutput(out, "evm%s" % i, command)
        self.matchclean(out, "ut", command)

    def testhost(self):
        command = "search machine --hostname ut3c5n10.aqd-unittest.ms.com"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "DnsRecord ut3c5n10.aqd-unittest.ms.com, "
                              "DNS environment internal not found.", command)

        command = "search machine --hostname server1.aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "ut9s03p1", command)
        self.matchclean(out, "ut3c5n10", command)
        self.matchclean(out, "ut3c5n6", command)

    def testhost_not_found(self):
        hostname = 'not_there.msad.ms.com'
        command = "search machine --hostname %s" % hostname
        self.notfoundtest(command.split(" "))
        command = "search machine --hostname %s --fullinfo" % hostname
        self.notfoundtest(command.split(" "))

    def testmemory(self):
        command = "search machine --memory 8192"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "ut3c5n10", command)
        self.matchoutput(out, "evm1", command)
        # Has a different memory amount...
        self.matchclean(out, "ut9s03p1", command)

    def testfullinfo(self):
        command = "search machine --machine evm1 --fullinfo"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Machine: evm1", command)
        self.matchoutput(out, "Model Type: virtual_machine", command)
        self.matchoutput(out, "Hosted by: ESX Cluster utecl1", command)
        self.matchoutput(out, "Vendor: utvendor Model: utmedium", command)

    def testexactcpu(self):
        command = ["search_machine", "--cpuname=l5520", "--cpuvendor=intel"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm1", command)
        self.matchclean(out, "ut9s03p1", command)
        self.matchclean(out, "ut3c5n10", command)

    def testexactcpufailvendor(self):
        command = ["search_machine", "--cpuname=l5520",
                   "--cpuvendor=vendor-does-not-exist"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Vendor vendor-does-not-exist not found.",
                         command)

    def testpartialcpufailvendor(self):
        command = ["search_machine", "--cpuvendor=vendor-does-not-exist"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Vendor vendor-does-not-exist not found.",
                         command)

    def testcpuname(self):
        command = ["search_machine", "--cpuname=l5520"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm1", command)
        self.matchclean(out, "ut9s03p1", command)
        self.matchclean(out, "ut3c5n10", command)

    def testsharedeprecated(self):
        command = ["search_machine", "--share=test_share_1"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm1", command)
        self.matchclean(out, "evm2", command)
        self.matchclean(out, "evm10", command)

    def testclustershare(self):
        # Share bound to cluster
        command = ["search_machine", "--disk_share=test_share_1"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm1", command)
        self.matchclean(out, "evm2", command)
        self.matchclean(out, "evm10", command)

    def testmetaclustershare(self):
        # Share bound to metacluster
        command = ["search_machine", "--disk_share=test_v2_share"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm40", command)
        self.matchclean(out, "evm1", command)
        self.matchclean(out, "evm2", command)

    def testsharebad(self):
        command = ["search_machine", "--share", "no-such-share"]
        out = self.notfoundtest(command)
        self.matchoutput(out, "No shares found with name no-such-share.",
                         command)

    def testdiskname(self):
        command = ["search_machine", "--disk_name", "c0d0"]
        out = self.commandtest(command)
        self.matchoutput(out, "ut3c1n3", command)
        self.matchclean(out, "ut3c5n10", command)
        self.matchclean(out, "evm", command)

    def testdiskctrl(self):
        command = ["search_machine", "--disk_name", "c0d0",
                   "--disk_controller", "scsi"]
        self.noouttest(command)

    def testdiskwwn(self):
        # Add some separators and uppercase letters to the mix
        command = ["search_machine", "--disk_wwn",
                   "60:05:08:b112233445566778899aabbCCD"]
        out = self.commandtest(command)
        self.matchoutput(out, "ut3c1n3", command)
        self.matchclean(out, "ut3c5n10", command)
        self.matchclean(out, "evm", command)

    def testdiskaddress(self):
        command = ["search_machine", "--disk_address", "0:0:1:0"]
        out = self.commandtest(command)
        self.matchoutput(out, "ut3c5n10", command)
        self.matchclean(out, "ut3c1n3", command)
        self.matchclean(out, "evm", command)

    def testip(self):
        ip = self.net["unknown0"].usable[2]
        command = ["search_machine", "--ip=%s" % ip]
        out = self.commandtest(command)
        self.matchoutput(out, "ut3c1n3", command)

    def testclusterpg(self):
        command = ["search_machine", "--cluster", "utecl8", "--pg", "user-v710"]
        out = self.commandtest(command)
        self.searchoutput(out, r"evm19$", command)

        # These are bound to user-v710, but on different clusters
        self.matchclean(out, "evm10", command)
        self.matchclean(out, "evm14", command)
        self.matchclean(out, "evm23", command)

        # These are on utecl8, but different pg
        self.matchclean(out, "evm20", command)
        self.matchclean(out, "evm21", command)

    def testpgwildcard(self):
        command = ["search_machine", "--pg", "user"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm10", command)
        self.matchoutput(out, "evm14", command)
        self.matchoutput(out, "evm19", command)
        self.matchoutput(out, "evm20", command)
        self.matchoutput(out, "evm21", command)
        self.matchoutput(out, "evm23", command)
        self.matchclean(out, "ut11s01", command)
        self.matchclean(out, "ut12s02", command)

    def testphyspg(self):
        command = ["search_machine", "--pg", "storage-v701"]
        out = self.commandtest(command)
        for port in range(1, 13):
            for template in ['ut11s01p%d', 'ut12s02p%d']:
                self.matchoutput(out, template % port, command)
        self.matchclean(out, "evm", command)

    def testnetworkip(self):
        command = ["search_machine", "--networkip", self.net["ut01ga2s01_v710"].ip]
        out = self.commandtest(command)
        self.searchoutput(out, r"evm10$", command)
        self.searchoutput(out, r"evm14$", command)
        self.matchclean(out, "evm11", command)
        self.matchclean(out, "evm15", command)
        self.matchclean(out, "evm17", command)

    def testmetacluster(self):
        command = "search machine --metacluster utmc8"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "evm40", command)
        self.matchoutput(out, "evm41", command)
        self.matchoutput(out, "evm42", command)
        self.matchclean(out, "ut14s1p0", command)

    def testused(self):
        command = ["search_machine", "--used"]
        out = self.commandtest(command)
        self.matchoutput(out, "ut9s03p1", command)
        self.matchoutput(out, "ut3c5n10", command)
        self.matchclean(out, "ut3c1n9", command)
        self.matchclean(out, "utnorack", command)

    def testunused(self):
        command = ["search_machine", "--unused"]
        out = self.commandtest(command)
        self.matchoutput(out, "evm2", command)
        self.matchoutput(out, "ut3c1n9", command)
        self.matchoutput(out, "utnorack", command)
        self.matchclean(out, "ut9s03p1", command)
        self.matchclean(out, "ut3c5n10", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchMachine)
    unittest.TextTestRunner(verbosity=2).run(suite)
