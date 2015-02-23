#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013  Contributor
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
"""Module for testing the update address alias command."""

if __name__ == '__main__':
    import utils
    utils.import_depends()

import unittest2 as unittest
from brokertest import TestBrokerCommand


class TestUpdateAddressAlias(TestBrokerCommand):

    def test_100_update_to_add_comment(self):
        command = ["update", "address",  "alias",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "arecord13.aqd-unittest.ms.com",
                   "--comments", "add a comment"]
        self.noouttest(command)

    def test_120_verify_add_comment(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "arecord13.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Comments: add a comment", command)

    def test_130_update_to_change_comment(self):
        command = ["update", "address",  "alias",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com",
                   "--comments", "update a comment"]
        self.noouttest(command)

    def test_140_verify_update_to_change_comment(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "Comments: update a comment", command)

    def test_150_update_to_no_comment(self):
        command = ["update", "address", "alias",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com",
                   "--comments", ""]
        self.noouttest(command)

    def test_160_verify_update_to_no_comment(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchclean(out, "Comments:", command)

    def test_200_update_nonexistent_fqdn(self):
        command = ["update", "address", "alias",
                   "--fqdn", "nonexistent.aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com",
                   "--comments", "nonexistent alias"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Fqdn nonexistent, DNS environment internal, "
                         "DNS domain aqd-unittest.ms.com not found.",
                         command)

    def test_230_update_nonexistent_address_alias(self):
        command = ["update", "address", "alias",
                   "--fqdn", "arecord13.aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com",
                   "--comments", "nonexistent alias"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Address Alias arecord13.aqd-unittest.ms.com, "
                         "fqdn arecord14.aqd-unittest.ms.com not found.",
                         command)

    def test_250_update_nonexistent_target(self):
        command = ["update", "address", "alias",
                   "--fqdn", "addralias1.aqd-unittest.ms.com",
                   "--target", "nonexistent.aqd-unittest.ms.com",
                   "--comments", "nonexistent target"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Fqdn nonexistent, DNS environment internal, "
                         "DNS domain aqd-unittest.ms.com not found.",
                         command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUpdateAddressAlias)
    unittest.TextTestRunner(verbosity=2).run(suite)
