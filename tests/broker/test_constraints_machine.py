#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2012,2013,2014,2015,2016  Contributor
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
"""Module for testing constraints in commands involving machine."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestMachineConstraints(TestBrokerCommand):

    def testdelmachinewithhost(self):
        command = "del machine --machine ut3c5n10"
        out = self.badrequesttest(command.split(" "))
        self.matchoutput(out, "Host unittest02.one-nyp.ms.com is still using "
                         "the machine, so the machine cannot be deleted.",
                         command)

    def testverifydelmachinewithhostfailed(self):
        command = "show machine --machine ut3c5n10"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Machine: ut3c5n10", command)
        self.matchoutput(out, "Model Type: blade", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMachineConstraints)
    unittest.TextTestRunner(verbosity=2).run(suite)
