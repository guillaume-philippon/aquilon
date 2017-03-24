#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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
"""Module for testing constraints in commands involving clusters."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestClusterConstraints(TestBrokerCommand):
    def test_100_del_cluster_with_machines(self):
        command = "del cluster --cluster utecl1"
        out = self.badrequesttest(command.split(" "))
        self.matchoutput(out, "ESX Cluster utecl1 is still in use by virtual "
                         "machines", command)

    def test_101_del_esx_cluster_with_machines(self):
        command = "del cluster --cluster utecl1"
        out = self.badrequesttest(command.split(" "))
        self.matchoutput(out, "ESX Cluster utecl1 is still in use by virtual "
                         "machines", command)

    def test_105_verify_utecl1(self):
        command = ["show_esx_cluster", "--cluster=utecl1"]
        out = self.commandtest(command)
        self.matchoutput(out, "ESX Cluster: utecl1", command)

    def test_110_del_clustered_host(self):
        command = ["del_host", "--hostname", "evh51.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Host evh51.aqd-unittest.ms.com is still a member of "
                         "ESX cluster utecl5, and cannot be deleted.  Please "
                         "remove it from the cluster first.",
                         command)

    def test_150_failrebindhost(self):
        command = ["cluster", "--cluster=utecl1",
                   "--host=evh1.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "cannot support VMs", command)

    def test_160_faildelshare(self):
        command = ["del_share", "--share", "test_share_1", "--cluster", "utecl1"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Share test_share_1 has virtual disks attached, "
                         "so it cannot be deleted.", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClusterConstraints)
    unittest.TextTestRunner(verbosity=2).run(suite)
