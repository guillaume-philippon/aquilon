#!/usr/bin/env python2.6
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2009,2010  Contributor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the EU DataGrid Software License.  You should
# have received a copy of the license with this program, and the
# license is published at
# http://eu-datagrid.web.cern.ch/eu-datagrid/license.html.
#
# THE FOLLOWING DISCLAIMER APPLIES TO ALL SOFTWARE CODE AND OTHER
# MATERIALS CONTRIBUTED IN CONNECTION WITH THIS PROGRAM.
#
# THIS SOFTWARE IS LICENSED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE AND ANY WARRANTY OF NON-INFRINGEMENT, ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. THIS
# SOFTWARE MAY BE REDISTRIBUTED TO OTHERS ONLY BY EFFECTIVELY USING
# THIS OR ANOTHER EQUIVALENT DISCLAIMER AS WELL AS ANY OTHER LICENSE
# TERMS THAT MAY APPLY.
"""Module for testing the make command."""

import os
import re
import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestMake(TestBrokerCommand):

    def testmakevmhosts(self):
        for i in range(1, 6):
            command = ["make", "--hostname", "evh%s.aqd-unittest.ms.com" % i,
                       "--os", "esxi/4.0.0", "--buildstatus", "rebuild"]
            (out, err) = self.successtest(command)
            self.matchclean(err, "removing binding", command)

            self.assert_(os.path.exists(os.path.join(
                self.config.get("broker", "profilesdir"),
                "evh1.aqd-unittest.ms.com%s" % self.profile_suffix)))

            self.failUnless(os.path.exists(os.path.join(
                self.config.get("broker", "builddir"),
                "domains", "unittest", "profiles",
                "evh1.aqd-unittest.ms.com.tpl")))

            servicedir = os.path.join(self.config.get("broker", "plenarydir"),
                                      "servicedata")
            results = self.grepcommand(["-rl", "evh%s.aqd-unittest.ms.com" % i,
                                        servicedir])
            self.failUnless(results, "No service plenary data that includes"
                                     "evh%s.aqd-unittest.ms.com" % i)

    def testmake10gighosts(self):
        for i in range(51, 75):
            command = ["make", "--hostname", "evh%s.aqd-unittest.ms.com" % i]
            (out, err) = self.successtest(command)

    def testfailwindows(self):
        command = ["make", "--hostname", "unittest01.one-nyp.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "is not a compilable archetype", command)

    def testmakeccisshost(self):
        command = ["make", "--hostname=unittest18.aqd-unittest.ms.com"]
        (out, err) = self.successtest(command)
        self.matchoutput(err, "1/1 compiled", command)

    def testmakezebra(self):
        command = ["make", "--hostname", "unittest20.aqd-unittest.ms.com"]
        (out, err) = self.successtest(command)
        self.matchoutput(err, "1/1 compiled", command)

    def testverifyunittest20(self):
        eth1_ip = self.net.unknown[12].usable[0]
        eth1_1_ip = self.net.unknown[12].usable[3]
        zebra_ip = self.net.unknown[13].usable[0]
        broadcast = self.net.unknown[12].broadcast
        netmask = self.net.unknown[12].netmask
        gateway = self.net.unknown[12].gateway
        command = ["cat", "--hostname", "unittest20.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'"/system/network/vips" = nlist\(\s*'
                          r'"hostname", nlist\(\s*'
                          r'"interfaces", list\(\s*'
                          r'"eth0",\s*"eth1"\s*\),\s*'
                          r'"ip", "%s"\s*\)\s*\);' % zebra_ip,
                          command)
        self.searchoutput(out,
                          r'"eth1", nlist\(\s*'
                          r'"aliases", nlist\(\s*'
                          r'escape\("1"\), nlist\(\s*'
                          r'"broadcast", "%s",\s*'
                          r'"ip", "%s",\s*'
                          r'"netmask", "%s"\s*\)\s*\),\s*'
                          r'"bootproto", "static",\s*'
                          r'"broadcast", "%s",\s*'
                          r'"gateway", "%s",\s*'
                          r'"ip", "%s",\s*'
                          r'"netmask", "%s"\s*\)' %
                          (broadcast, eth1_1_ip, netmask,
                           broadcast, gateway, eth1_ip, netmask),
                          command)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMake)
    unittest.TextTestRunner(verbosity=2).run(suite)
