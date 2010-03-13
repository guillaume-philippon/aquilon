#!/usr/bin/env python2.5
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
"""Module for testing the del esx cluster command."""


import os
import sys
import unittest

if __name__ == "__main__":
    BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    SRCDIR = os.path.join(BINDIR, "..", "..")
    sys.path.append(os.path.join(SRCDIR, "lib", "python2.5"))

from brokertest import TestBrokerCommand


class TestDelESXCluster(TestBrokerCommand):

    def testdelutecl1(self):
        command = ["del_esx_cluster", "--cluster=utecl1"]
        self.noouttest(command)

    def testverifydelutecl1(self):
        command = ["show_esx_cluster", "--cluster=utecl1"]
        self.notfoundtest(command)

    def testdelutecl2(self):
        command = ["del_esx_cluster", "--cluster=utecl2"]
        self.noouttest(command)

    def testverifydelutecl2(self):
        command = ["show_esx_cluster", "--cluster=utecl2"]
        self.notfoundtest(command)

    def testdelutecl3(self):
        command = ["del_esx_cluster", "--cluster=utecl3"]
        self.noouttest(command)

    def testverifydelutecl3(self):
        command = ["show_esx_cluster", "--cluster=utecl3"]
        self.notfoundtest(command)

    def testdelutecl4(self):
        command = ["del_esx_cluster", "--cluster=utecl4"]
        self.noouttest(command)

    def testverifydelutecl4(self):
        command = ["show_esx_cluster", "--cluster=utecl4"]
        self.notfoundtest(command)

    def testdelutmc4(self):
        for i in range(5, 11):
            command = ["del_esx_cluster", "--cluster=utecl%d" % i]
            self.noouttest(command)

    def testverifyall(self):
        command = ["show_esx_cluster", "--all"]
        out = self.commandtest(command)
        self.matchclean(out, "esx cluster: utecl", command)

    def testdelnotfound(self):
        command = ["del_esx_cluster", "--cluster=esx_cluster-does-not-exist"]
        self.notfoundtest(command)

    def verifyplenaryclusterclient(self):
        for i in range(1, 5):
            cluster = "utecl%s" % i
            plenary = os.path.join(self.config.get("broker", "plenarydir"),
                                   "cluster", cluster, "client.tpl")
            self.failIf(os.path.exists(plenary),
                        "Plenary file '%s' still exists" % plenary)
            plenary = os.path.join(self.config.get("broker", "builddir"),
                                   "domains", "unittest", "profiles",
                                   "clusters", "%s.tpl" % cluster)
            self.failIf(os.path.exists(plenary),
                        "Plenary file '%s' still exists" % plenary)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelESXCluster)
    unittest.TextTestRunner(verbosity=2).run(suite)

