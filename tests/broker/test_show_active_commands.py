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
"""Module for testing the show active commands command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestShowActiveCommands(TestBrokerCommand):

    def testshowactivecommands(self):
        command = "show_active_commands"
        out = self.commandtest(command)
        self.matchoutput(out, "aq show_active_commands", command)
        self.matchclean(out, "aq status", command)
        lines = out.splitlines()
        self.assertEqual(1, len(lines),
                         "Expected only a single line, got %s:\n%s" %
                         (len(lines), out))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestShowActiveCommands)
    unittest.TextTestRunner(verbosity=2).run(suite)
