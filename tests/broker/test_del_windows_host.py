#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2015,2016  Contributor
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
"""Module for testing the del windows host command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDelWindowsHost(TestBrokerCommand):

    def testfailnonwindows(self):
        command = "del windows host --hostname unittest00.one-nyp.ms.com"
        err = self.badrequesttest(command.split(" "))
        self.matchoutput(err,
                         "Host unittest00.one-nyp.ms.com "
                         "has archetype aquilon, expected windows.",
                         command)

    def testdelunittest01(self):
        self.dsdb_expect_delete(self.net["unknown0"].usable[10])
        command = "del windows host --hostname unittest01.one-nyp.ms.com"
        self.statustest(command.split(" "))
        self.dsdb_verify()
        self.check_plenary_gone("hostdata", "unittest01.one-nyp.ms.com")

    def testverifydelunittest01(self):
        command = "show host --hostname unittest01.one-nyp.ms.com"
        self.notfoundtest(command.split(" "))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelWindowsHost)
    unittest.TextTestRunner(verbosity=2).run(suite)
