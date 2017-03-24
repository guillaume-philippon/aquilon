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
"""Module for testing the update_cluster --metacluster command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestRebindMetaCluster(TestBrokerCommand):

    def testfailinvalidcluster(self):
        command = ["update_cluster", "--cluster=cluster-does-not-exist",
                   "--metacluster=utmc1"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Cluster cluster-does-not-exist not found.",
                         command)

    def testfailinvalidmetacluster(self):
        command = ["update_cluster", "--cluster=utecl1",
                   "--metacluster=metacluster-does-not-exist"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Metacluster metacluster-does-not-exist not found.",
                         command)

    def testfailfullmetacluster(self):
        command = ["update_cluster", "--cluster=utecl4", "--metacluster=utmc3"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Metacluster utmc3 has 1 clusters bound, which "
                         "exceeds the requested limit of 0.", command)

    def testfailrebindsandboxcl1(self):
        command = ["update_cluster", "--cluster=sandboxcl1",
                   "--metacluster=utmc1"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "ESX Cluster sandboxcl1 sandbox %s/"
                         "utsandbox does not match ESX metacluster utmc1 "
                         "domain unittest." % self.user, command)

    def testrebindutecl3(self):
        command = ["update_cluster", "--cluster=utecl3", "--metacluster=utmc1"]
        self.noouttest(command)

    def testverifyrebindutecl3(self):
        command = ["cat", "--cluster=utecl3", "--data"]
        out = self.commandtest(command)
        self.matchoutput(out, "structure template clusterdata/utecl3;", command)
        self.matchoutput(out, '"system/cluster/name" = "utecl3";', command)
        self.matchoutput(out, '"system/cluster/metacluster/name" = "utmc1";', command)
        self.matchoutput(out, '"system/metacluster/name" = "utmc1";', command)
        self.matchclean(out, "resources/virtual_machine", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRebindMetaCluster)
    unittest.TextTestRunner(verbosity=2).run(suite)
