#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2012,2013,2015,2016  Contributor
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
"""Module for testing constraints available after cluster creation."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestClusterConstraintsNoMembers(TestBrokerCommand):

    def test_100_reconfigure_utecl1_members(self):
        # Check if reconfiguring an empty list does nothing
        command = ["reconfigure", "--membersof", "utecl1"]
        self.noouttest(command)

    def test_200_add_vm_without_vmhost(self):
        command = ["add_machine", "--machine=evm1", "--model=utmedium",
                   "--cluster=utecl1"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "cannot support VMs", command)

    def test_200_try_fix_location(self):
        command = ["update_cluster", "--cluster", "utecl5", "--fix_location"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Cannot infer the cluster location from the "
                         "host locations.", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestClusterConstraintsNoMembers)
    unittest.TextTestRunner(verbosity=2).run(suite)
