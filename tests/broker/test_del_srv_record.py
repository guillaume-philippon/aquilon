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
"""Module for testing the del srv record command."""

import unittest

if __name__ == '__main__':
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDelSrvRecord(TestBrokerCommand):

    def test_100_del_target(self):
        command = ["del", "srv", "record", "--service", "kerberos",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_110_verify_others(self):
        command = ["search", "dns", "--record_type", "srv"]
        out = self.commandtest(command)
        self.matchoutput(out, "_kerberos._tcp.aqd-unittest.ms.com", command)
        self.matchoutput(out, "_ldap._tcp.aqd-unittest.ms.com", command)

    def test_120_del_nonexistent_target(self):
        command = ["del", "srv", "record", "--service", "kerberos",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com",
                   "--target", "arecord14.aqd-unittest.ms.com"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "SRV Record for service kerberos, protocol tcp in DNS "
                         "domain aqd-unittest.ms.com, with target "
                         "arecord14.aqd-unittest.ms.com not found.",
                         command)

    def test_130_del_notarget(self):
        command = ["del", "srv", "record", "--service", "kerberos",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_140_del_ldap(self):
        command = ["del", "srv", "record", "--service", "ldap",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_145_del_restricted_target(self):
        command = ["del", "srv", "record", "--service", "ldap-restrict",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_146_verify_target_gone(self):
        command = ["search", "dns", "--fullinfo",
                   "--fqdn", "ldap.restrict.aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_147_del_reserved_target(self):
        command = ["del", "srv", "record", "--service", "ldap-reserved",
                   "--protocol", "udp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_148_del_alias_target(self):
        command = ["del", "srv", "record", "--service", "ldap-alias",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_149_del_addr_alias_target(self):
        command = ["del", "srv", "record", "--service", "http",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_300_del_record_with_grn(self):
        command = ["del", "srv", "record", "--service", "sip",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_305_verify_del_record_with_grn(self):
        command = ["show", "srv", "record", "--service", "sip",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_310_del_tls_srvrec(self):
        command = ["del", "srv", "record", "--service", "collab",
                   "--protocol", "tls", "--dns_domain", "aqd-unittest.ms.com"]
        self.noouttest(command)

    def test_315_verify_del_tls_srvrec(self):
        command = ["show", "srv", "record", "--service", "collab",
                   "--protocol", "tls", "--dns_domain", "aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_320_del_with_dns_env(self):
        command = ["del", "srv", "record", "--service", "collab",
                   "--protocol", "tls", "--dns_domain", "aqd-unittest.ms.com",
                   "--dns_environment", "ut-env"]
        self.noouttest(command)

    def test_325_verify_del_with_dns_env(self):
        command = ["show", "srv", "record", "--service", "collab",
                   "--protocol", "tls", "--dns_domain", "aqd-unittest.ms.com",
                   "--dns_environment", "ut-env"]
        self.notfoundtest(command)

    def test_330_del_with_diff_target_env(self):
        command = ["del", "srv", "record", "--service", "collab2",
                   "--protocol", "tls", "--dns_domain", "aqd-unittest.ms.com",
                   "--dns_environment", "internal",
                   "--target", "addralias1.aqd-unittest-ut-env.ms.com",
                   "--target_environment", "ut-env"]
        self.noouttest(command)

    def test_335_verify_del_with_dff_target_dns_env(self):
        command = ["show", "srv", "record", "--service", "collab2",
                   "--protocol", "tls", "--dns_domain", "aqd-unittest.ms.com",
                   "--dns_environment", "internal"]
        self.notfoundtest(command)

    def test_400_verify_allgone(self):
        command = ["search", "dns", "--record_type", "srv"]
        self.noouttest(command)

    def test_410_del_nonexistent(self):
        command = ["del", "srv", "record", "--service", "kerberos",
                   "--protocol", "tcp", "--dns_domain", "aqd-unittest.ms.com"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "SRV Record for service kerberos, protocol tcp in DNS "
                         "domain aqd-unittest.ms.com not found.",
                         command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelSrvRecord)
    unittest.TextTestRunner(verbosity=2).run(suite)
