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
"""Module for testing the del bunker command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDelBunker(TestBrokerCommand):

    def test_100_add_bunker_net(self):
        self.net.allocate_network(self, "bucket1.ut_net", 24, "unknown",
                                  "bunker", "bucket1.ut",
                                  comments="Made-up network")

    def test_101_del_utbunker1_fail(self):
        command = "del bunker --bunker bucket1.ut"
        err = self.badrequesttest(command.split(" "))
        self.matchoutput(err,
                         "Bad Request: Could not delete bunker bucket1.ut, networks "
                         "were found using this location.",
                         command)

    def test_102_cleanup_bunker_net(self):
        self.net.dispose_network(self, "bucket1.ut_net")

    def test_110_del_utbunker1(self):
        command = "del bunker --bunker bucket1.ut"
        self.noouttest(command.split(" "))

    def test_200_del_bunker_notexist(self):
        command = "del bunker --bunker bunker-does-not-exist"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "Bunker bunker-does-not-exist not found.", command)

    def test_300_verify_del_utbunker1(self):
        command = "show bunker --bunker bucket1.ut"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "Bunker bucket1.ut not found.", command)

    def test_300_show_all(self):
        command = ["show_bunker", "--all"]
        out = self.commandtest(command)
        self.matchclean(out, "bucket1.ut", command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelBunker)
    unittest.TextTestRunner(verbosity=2).run(suite)
