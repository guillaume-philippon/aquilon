#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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
"""Module for testing the add dns domain command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestAddDnsDomain(TestBrokerCommand):

    def testaddaqdunittestdomain(self):
        self.dsdb_expect("add_dns_domain -domain_name aqd-unittest.ms.com "
                         "-comments Some DNS domain comments")
        self.noouttest(["add", "dns_domain", "--dns_domain", "aqd-unittest.ms.com",
                        "--comments", "Some DNS domain comments"])
        self.dsdb_verify()

    def testaddaqdunittest_ut_env_domain(self):
        self.dsdb_expect("add_dns_domain -domain_name aqd-unittest-ut-env.ms.com "
                         "-comments Some DNS domain comments")
        self.noouttest(["add", "dns_domain", "--dns_domain", "aqd-unittest-ut-env.ms.com",
                        "--comments", "Some DNS domain comments"])
        self.dsdb_verify()

    def testaddcardsdomain(self):
        self.dsdb_expect("add_dns_domain -domain_name cards.example.com "
                         "-comments A pack of lies")
        self.noouttest(["add", "dns_domain",
                        "--dns_domain", "cards.example.com",
                        "--comments", "A pack of lies"])
        self.dsdb_verify()

    def testaddrestricteddomain(self):
        self.dsdb_expect("add_dns_domain -domain_name restrict.aqd-unittest.ms.com "
                         "-comments ")
        self.noouttest(["add", "dns_domain", "--dns_domain", "restrict.aqd-unittest.ms.com",
                        "--restricted"])
        self.dsdb_verify()

    def testverifyaddaqdunittestdomain(self):
        command = "show dns_domain --dns_domain aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.output_equals(out, """
            DNS Domain: aqd-unittest.ms.com
              Restricted: False
              Comments: Some DNS domain comments
            """, command)

    def testverifyaddaqdunittestdomaincsv(self):
        command = "show dns_domain --dns_domain aqd-unittest.ms.com --format=csv"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "aqd-unittest.ms.com,Some DNS domain comments",
                         command)

    def testverifyaddrestricteddomain(self):
        command = "show dns_domain --dns_domain restrict.aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.output_equals(out, """
            DNS Domain: restrict.aqd-unittest.ms.com
              Restricted: True
            """, command)

    def testverifyaddrestricteddomainproto(self):
        command = ["show_dns_domain",
                   "--dns_domain", "restrict.aqd-unittest.ms.com",
                   "--format", "proto"]
        domain = self.protobuftest(command, expect=1)[0]
        self.assertEqual(domain.name, "restrict.aqd-unittest.ms.com")
        self.assertEqual(domain.restricted, True)

    def testverifyaddaqdunittestdomainproto(self):
        command = ["show", "dns_domain", "--dns_domain=aqd-unittest.ms.com",
                   "--format=proto"]
        msgs = self.protobuftest(command, expect=1)
        domain = msgs[0]
        self.assertEqual(domain.name, 'aqd-unittest.ms.com')
        self.assertEqual(domain.restricted, False)

    def testaddtoolongdomain(self):
        command = ['add', 'dns_domain', '--dns_domain',
                   #         1         2         3         4         5         6
                   's234567890123456789012345678901234567890123456789012345678901234' +
                   '.ms.com']
        out = self.badrequesttest(command)
        self.matchoutput(out, "DNS name components must have a length between "
                         "1 and 63.", command)

    def testaddtopleveldomain(self):
        command = ['add', 'dns_domain', '--dns_domain', 'toplevel']
        out = self.badrequesttest(command)
        self.matchoutput(out, "Top-level DNS domains cannot be added.", command)

    def testaddinvaliddomain(self):
        command = ['add', 'dns_domain', '--dns_domain', 'foo-.ms.com']
        out = self.badrequesttest(command)
        self.matchoutput(out, "Illegal DNS name format 'foo-'.", command)

    def testverifyshowall(self):
        command = "show dns_domain --all"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "DNS Domain: aqd-unittest.ms.com", command)
        self.matchoutput(out, "DNS Domain: aqd-unittest-ut-env.ms.com", command)

    def testverifyshowallproto(self):
        command = "show dns_domain --all --format=proto"
        dns_domains = self.protobuftest(command.split(" "))
        dns_names = [d.name for d in dns_domains]
        for domain in ['ms.com', 'aqd-unittest.ms.com', 'aqd-unittest-ut-env.ms.com']:
            self.assertIn(domain, dns_names)

    def testaddcolodomains(self):
        self.dsdb_expect("add_dns_domain -domain_name excx.aqd-unittest.ms.com "
                         "-comments ")
        command = ["add", "dns", "domain",
                   "--dns_domain", "excx.aqd-unittest.ms.com"]
        self.noouttest(command)

        self.dsdb_expect("add_dns_domain -domain_name utcolo.aqd-unittest.ms.com "
                         "-comments ")
        command = ["add", "dns", "domain",
                   "--dns_domain", "utcolo.aqd-unittest.ms.com"]
        self.noouttest(command)

        self.dsdb_verify()

    def testaddlocaldomain(self):
        hostname = self.config.get('unittest', 'hostname')
        _, _, domain = hostname.partition('.')
        # If the local host is under .ms.com, then we don't want to add it again
        p, _, _ = self.runcommand(["show", "dns", "domain",
                                   "--dns_domain", domain])
        if domain and p.returncode == 4:
            self.dsdb_expect("add_dns_domain -domain_name %s -comments " % domain)
            command = ["add", "dns", "domain", "--dns_domain", domain]
            self.noouttest(command)
            self.dsdb_verify()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddDnsDomain)
    unittest.TextTestRunner(verbosity=2).run(suite)
