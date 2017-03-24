#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2016  Contributor
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
"""Module for testing the del intervention command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDelIntervention(TestBrokerCommand):

    def test_100_del_intervention(self):
        path = ["resource", "host", "server1.aqd-unittest.ms.com",
                "intervention", "i1", "config"]
        self.check_plenary_exists(*path)
        command = ["del_intervention", "--intervention=i1",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)
        self.check_plenary_gone(*path)

        path = ["resource", "host", "server1.aqd-unittest.ms.com",
                "intervention", "blank", "config"]
        self.check_plenary_exists(*path)
        command = ["del_intervention", "--intervention=bLaNk",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)
        self.check_plenary_gone(*path)

        command = ["del_intervention", "--intervention=groups",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)

        command = ["del_intervention", "--intervention=disable",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelIntervention)
    unittest.TextTestRunner(verbosity=2).run(suite)
