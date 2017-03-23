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
"""Module for testing the unmap service command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestUnmapService(TestBrokerCommand):

    def testunmapafs(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--justification", "tcm=12345678",
                        "--service", "afs", "--instance", "q.ny.ms.com"])
        self.noouttest(["unmap", "service", "--city", "ex",
                        "--justification", "tcm=12345678",
                        "--service", "afs", "--instance", "q.ny.ms.com"])
        self.noouttest(["unmap", "service", "--building", "np",
                        "--justification", "tcm=12345678",
                        "--service", "afs", "--instance", "q.ny.ms.com"])

    def testverifyunmapafs(self):
        command = ["show_map",
                   "--service=afs", "--instance=q.ny.ms.com", "--building=ut"]
        self.notfoundtest(command)

        command = ["show_map", "--service=afs", "--instance=q.ny.ms.com"]
        self.noouttest(command)

    def testunmapafsbynet(self):
        ip = self.net["netsvcmap"].subnet()[0].ip
        self.noouttest(["unmap", "service", "--networkip", ip,
                        "--service", "afs", "--instance", "afs-by-net",
                        "--justification", "tcm=12345678"])

    def testverifyunmapafsbynet(self):
        ip = self.net["netsvcmap"].subnet()[0].ip
        command = ["show_map",
                   "--service=afs", "--instance=afs-by-net",
                   "--networkip=%s" % ip]
        self.notfoundtest(command)

        command = ["show_map", "--service=afs", "--instance=afs-by-net"]
        self.noouttest(command)

    def testunmapafsbynetpers(self):
        ip = self.net["netperssvcmap"].subnet()[0].ip
        self.noouttest(["unmap", "service", "--networkip", ip,
                        "--service", "scope_test", "--instance", "scope-network",
                        "--personality", "utpers-dev",
                        "--archetype", "aquilon"])

        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "scope_test",
                        "--instance", "target-personality",
                        "--personality", "utpers-dev",
                        "--archetype", "aquilon"])

        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "scope_test",
                        "--instance", "target-dev",
                        "--host_environment", "dev"])

        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "scope_test", "--instance", "scope-building",
                        "--justification", "tcm=12345678"])

    def testverifyunmapafsbynetpers(self):
        ip = self.net["netperssvcmap"].subnet()[0].ip
        command = ["show_map",
                   "--service=scope_test", "--instance=scope-network",
                   "--networkip=%s" % ip, "--personality", "compileserver",
                   "--archetype", "aquilon"]
        self.notfoundtest(command)

        command = ["show_map", "--service=scope_test", "--instance=scope-network"]
        self.noouttest(command)

        command = ["show_map", "--service=scope_test", "--instance=scope-building"]
        self.noouttest(command)

    def testunmapdns(self):
        self.noouttest(["unmap", "service", "--hub", "ny",
                        "--justification", "tcm=12345678",
                        "--service", "dns", "--instance", "unittest"])

    def testverifyunmapdns(self):
        command = ["show_map",
                   "--service=dns", "--instance=unittest", "--hub=ny"]
        self.notfoundtest(command)

    def testunmapaqd(self):
        self.noouttest(["unmap", "service", "--campus", "ny",
                        "--justification", "tcm=12345678",
                        "--service", "aqd", "--instance", "ny-prod"])
        self.noouttest(["unmap", "service", "--city", "ex",
                        "--justification", "tcm=12345678",
                        "--service", "aqd", "--instance", "ny-prod"])

    def testverifyunmapaqd(self):
        command = ["show_map",
                   "--service=aqd", "--instance=ny-prod", "--campus=ny"]
        self.notfoundtest(command)

        command = ["show_map",
                   "--service=aqd", "--instance=ny-prod", "--city=ex"]
        self.notfoundtest(command)

    def testunmaplemon(self):
        self.noouttest(["unmap", "service", "--campus", "ny",
                        "--justification", "tcm=12345678",
                        "--service", "lemon", "--instance", "ny-prod"])
        self.noouttest(["unmap", "service", "--city", "ex",
                        "--justification", "tcm=12345678",
                        "--service", "lemon", "--instance", "ny-prod"])

    def testverifyunmaplemon(self):
        command = ["show_map",
                   "--service=lemon", "--instance=ny-prod", "--campus=ny"]
        self.notfoundtest(command)

        command = ["show_map",
                   "--service=lemon", "--instance=ny-prod", "--city=ex"]
        self.notfoundtest(command)

    def testunmapbootserver(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--justification", "tcm=12345678",
                        "--service", "bootserver", "--instance", "one-nyp"])
        self.noouttest(["unmap", "service", "--building", "cards",
                        "--justification", "tcm=12345678",
                        "--service", "bootserver", "--instance", "one-nyp"])
        self.noouttest(["unmap", "service", "--building", "np",
                        "--justification", "tcm=12345678",
                        "--service", "bootserver", "--instance", "one-nyp"])

    def testverifyunmapbootserver(self):
        command = ["show_map", "--service=bootserver", "--instance=one-nyp",
                   "--building=ut"]
        self.notfoundtest(command)
        command = ["show_map", "--service=bootserver", "--instance=one-nyp",
                   "--building=cards"]
        self.notfoundtest(command)

    # we unmap ntp for the ex city because we want to tear that city down
    # separately, but we leave the ntp mappings everywhere else in order
    # to later test that the maps are correctly dropped when we delete
    # the serviceinstance
    def testunmapntp(self):
        self.noouttest(["unmap", "service", "--city", "ex",
                        "--justification", "tcm=12345678",
                        "--service", "ntp", "--instance", "pa.ny.na"])

    def testverifyunmapntp(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=ntp", "--instance=pa.ny.na", "--city=ex"]
        self.notfoundtest(command)

    def testunmapsyslogng(self):
        self.noouttest(["unmap", "service", "--campus", "ny",
                        "--justification", "tcm=12345678",
                        "--service", "syslogng", "--instance", "ny-prod"])

    def testverifyunmapsyslogng(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=syslogng", "--instance=ny-prod", "--campus=ny"]
        self.notfoundtest(command)

    def testunmaputsi1(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--justification", "tcm=12345678",
                        "--service", "utsvc", "--instance", "utsi1"])
        self.noouttest(["unmap", "service", "--building", "np",
                        "--justification", "tcm=12345678",
                        "--service", "utsvc", "--instance", "utsi1"])
        self.noouttest(["unmap", "service", "--building", "cards",
                        "--justification", "tcm=12345678",
                        "--service", "utsvc", "--instance", "utsi1"])

    def testverifyunmaputsi1(self):
        command = ["show_map",
                   "--service=utsvc", "--instance=utsi1", "--building=ut"]
        self.notfoundtest(command)
        command = ["show_map",
                   "--service=utsvc", "--instance=utsi1", "--building=cards"]
        self.notfoundtest(command)

    def testunmaputsi2(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--justification", "tcm=12345678",
                        "--service", "utsvc", "--instance", "utsi2"])
        self.noouttest(["unmap", "service", "--building", "np",
                        "--justification", "tcm=12345678",
                        "--service", "utsvc", "--instance", "utsi2"])

    def testverifyunmaputsi2(self):
        command = ["show_map",
                   "--service=utsvc", "--instance=utsi2", "--building=ut"]
        self.notfoundtest(command)

    def testunmapchooser(self):
        for service in ["chooser1", "chooser2", "chooser3"]:
            for n in ['a', 'b', 'c']:
                if service == 'chooser2' and n == 'b':
                    continue
                if service == 'chooser3' and n == 'c':
                    continue
                instance = "ut.%s" % n
                self.noouttest(["unmap", "service", "--building", "ut",
                                "--justification", "tcm=12345678",
                                "--service", service, "--instance", instance])

    def testunmapwithpersona(self):
        self.noouttest(["unmap", "service", "--organization", "ms", "--service",
                        "utsvc", "--instance", "utsi2", "--archetype",
                        "aquilon", "--personality", "utunused/dev"])

    def testverifyunmapwithpersona(self):
        command = ["show_map", "--archetype=aquilon",
                   "--personality=utunused/dev", "--service=utsvc"]
        out = self.commandtest(command)
        self.matchoutput(out, "", command)

    # TODO: If/when there is another mapped personality, explicitly skip
    # the unmap operation to test that del_service automatically removes
    # the mapping.

    def testunmapesx(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "esx_management_server",
                        "--instance", "ut.a", "--archetype", "vmhost",
                        "--personality", "vulcan-10g-server-prod",
                        "--justification", "tcm=12345678"])
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "esx_management_server",
                        "--instance", "ut.b", "--archetype", "vmhost",
                        "--personality", "vulcan-10g-server-prod",
                        "--justification", "tcm=12345678"])
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "vmseasoning", "--instance", "salt",
                        "--archetype", "vmhost",
                        "--personality", "vulcan-10g-server-prod",
                        "--justification", "tcm=12345678"])
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "vmseasoning", "--instance", "pepper",
                        "--archetype", "vmhost",
                        "--personality", "vulcan-10g-server-prod",
                        "--justification", "tcm=12345678"])

    def testverifyunmapesx(self):
        command = ["show_map", "--archetype=vmhost",
                   "--personality=vulcan-10g-server-prod", "--building=ut"]
        out = self.commandtest(command)
        self.matchclean(out, "Service: esx_management_server Instance: ut.a ",
                        command)
        self.matchclean(out, "Service: esx_management_server Instance: ut.b ",
                        command)
        self.matchclean(out, "Service: vmseasoning Instance: salt", command)
        self.matchclean(out, "Service: vmseasoning Instance: pepper", command)

    def testunmapwindowsfail(self):
        command = ["unmap", "service", "--organization", "ms",
                   "--service", "utsvc", "--instance", "utsi2",
                   "--archetype", "windows"]
        out = self.badoptiontest(command)
        self.matchoutput(out, "Not all mandatory options specified!", command)

    def testunmapgenericfail(self):
        command = ["unmap", "service", "--organization", "ms",
                   "--service", "utsvc", "--instance", "utsi2",
                   "--personality", "generic"]
        out = self.badoptiontest(command)
        self.matchoutput(out, "Not all mandatory options specified!", command)

    def testunmappollhelper(self):
        service = self.config.get("broker", "poll_helper_service")
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--justification", "tcm=12345678",
                        "--service", service, "--instance", "unittest"])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUnmapService)
    unittest.TextTestRunner(verbosity=2).run(suite)
