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
"""Module for testing the del alias command."""

import unittest

if __name__ == '__main__':
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand
from eventstest import EventsTestMixin


class TestDelAlias(EventsTestMixin, TestBrokerCommand):
    def test_100_del_alias2host(self):
        command = ["del", "alias", "--fqdn", "alias2host.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Alias alias2host.aqd-unittest.ms.com still has "
                         "aliases, delete them first.", command)

    def test_110_del_missing(self):
        command = ["del", "alias", "--fqdn", "no-such-alias.aqd-unittest.ms.com"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Alias no-such-alias.aqd-unittest.ms.com, DNS "
                         "environment internal not found.",
                         command)

    def test_200_del_alias4alias(self):
        command = ["del", "alias", "--fqdn", "alias4alias.aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_201_del_alias3alias(self):
        command = ["del", "alias", "--fqdn", "alias3alias.aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_202_del_alias2alias(self):
        command = ["del", "alias", "--fqdn", "alias2alias.aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_210_del_alias2host(self):
        self.event_del_dns('alias2host.aqd-unittest.ms.com')
        command = ["del", "alias", "--fqdn", "alias2host.aqd-unittest.ms.com"]
        self.noouttest(command)
        self.events_verify()

    def test_220_del_mscom_alias(self):
        self.event_del_dns('alias.ms.com')
        command = ["del", "alias", "--fqdn", "alias.ms.com"]
        self.dsdb_expect("delete_host_alias -alias_name alias.ms.com")
        self.noouttest(command)
        self.dsdb_verify()
        self.events_verify()

    def test_230_del_alias2diff_environment(self):
        command = ["del", "alias", "--fqdn", "alias2alias.aqd-unittest-ut-env.ms.com",
                   "--dns_environment", "ut-env"]
        self.noouttest(command)

    def test_235_del_alias2diff_environment(self):
        self.event_del_dns('alias2host.aqd-unittest-ut-env.ms.com', dns_enviornment='ut-env')
        command = ["del", "alias", "--fqdn", "alias2host.aqd-unittest-ut-env.ms.com",
                   "--dns_environment", "ut-env"]
        self.noouttest(command)
        self.events_verify()

    def test_238_del_alias2diff_environment(self):
        command = ["del", "alias", "--fqdn", "alias13.aqd-unittest.ms.com",
                   "--dns_environment", "ut-env"]
        self.noouttest(command)

    def test_300_del_restrict1(self):
        command = ["del", "alias", "--fqdn", "restrict1.aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_301_verify_target(self):
        # There was a second alias, so the target must still exist
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "target2.restrict.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         "Reserved Name: target2.restrict.aqd-unittest.ms.com",
                         command)

    def test_310_del_autotarget(self):
        command = ["del", "alias", "--fqdn", "restrict2.aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_311_verify_target_gone(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "target2.restrict.aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_320_restricted_alias_no_dsdb(self):
        command = ["del", "alias", "--fqdn", "restrict.ms.com"]
        self.noouttest(command)
        self.dsdb_verify(empty=True)

    def test_330_del_srv_alases(self):
        self.noouttest(["del_alias", "--fqdn", "srv-alias.one-nyp.ms.com"])
        self.noouttest(["del_alias", "--fqdn", "srv-alias2.one-nyp.ms.com"])

    def test_400_del_alias_added_with_grn(self):
        command = ["del", "alias", "--fqdn", "alias2host-grn.aqd-unittest.ms.com"]
        self.noouttest(command)
        self.dsdb_verify(empty=True)

    def test_405_verify_alias_with_grn_gone(self):
        command = ["search", "dns", "--fqdn", "alias2host-grn.aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_410_del_alias_added_with_eon_id(self):
        command = ["del", "alias", "--fqdn", "alias2host-eon-id.aqd-unittest.ms.com"]
        self.noouttest(command)
        self.dsdb_verify(empty=True)

    def test_415_verify_alias_with_eon_id_gone(self):
        command = ["search", "dns", "--fqdn", "alias2host-eon-id.aqd-unittest.ms.com"]
        self.notfoundtest(command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelAlias)
    unittest.TextTestRunner(verbosity=2).run(suite)
