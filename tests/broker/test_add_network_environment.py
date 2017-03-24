#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2015,2016  Contributor
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
"""Module for testing the add_network_environment command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestAddNetworkEnvironment(TestBrokerCommand):

    def test_100_add_excx(self):
        command = ["add", "network", "environment",
                   "--network_environment", "excx", "--building", "np",
                   "--dns_environment", "excx",
                   "--comments", "Some netenv comments"]
        self.noouttest(command)

    def test_105_show_excx(self):
        command = ["show", "network", "environment",
                   "--network_environment", "excx"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Network Environment: excx
              DNS Environment: excx
              Building: np
                Fullname: one-nyp
                Address: 1 NY Plaza
                Location Parents: [Organization ms, Hub ny, Continent na, Country us, Campus ny, City ny]
              Comments: Some netenv comments
            """, command)

    def test_110_add_utcolo(self):
        command = ["add", "network", "environment",
                   "--network_environment", "utcolo",
                   "--dns_environment", "ut-env",
                   "--comments", "Some other netenv comments"]
        self.noouttest(command)

    def test_115_show_utcolo(self):
        command = ["show", "network", "environment",
                   "--network_environment", "utcolo"]
        out = self.commandtest(command)
        self.output_equals(out, """
            Network Environment: utcolo
              DNS Environment: ut-env
                Comments: Some DNS env comments
              Comments: Some other netenv comments
            """, command)

    def test_120_add_cardenv(self):
        command = ["add", "network", "environment",
                   "--network_environment", "cardenv",
                   "--dns_environment", "ut-env",
                   "--comments", "Card network environment"]
        self.noouttest(command)

    def test_200_bad_name(self):
        command = ["add", "network", "environment",
                   "--dns_environment", "ut-env",
                   "--network_environment", "<badname>"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "'<badname>' is not a valid value for network environment",
                         command)

    def test_200_use_internal(self):
        command = ["add", "network", "environment",
                   "--network_environment", "not-internal",
                   "--dns_environment", "internal"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Only the default network environment may be "
                         "associated with the default DNS environment.",
                         command)

    def test_300_show_all(self):
        command = ["show", "network", "environment", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, "Network Environment: internal", command)
        self.matchoutput(out, "Network Environment: excx", command)
        self.matchoutput(out, "Network Environment: utcolo", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddNetworkEnvironment)
    unittest.TextTestRunner(verbosity=2).run(suite)
