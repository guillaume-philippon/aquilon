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
"""Module for testing constraints in commands involving DNS."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDnsConstraints(TestBrokerCommand):

    def testdelenvinuse(self):
        command = ["del", "dns", "environment", "--dns_environment", "ut-env"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "DNS Environment ut-env is still in use by DNS "
                         "records, and cannot be deleted.", command)

    def testdelaliasedaddress(self):
        command = ["del", "address", "--fqdn", "arecord13.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "DNS Record arecord13.aqd-unittest.ms.com still has "
                         "aliases, delete them first.",
                         command)

    def testdelaliasedalias(self):
        command = ["del", "alias", "--fqdn", "alias2host.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Alias alias2host.aqd-unittest.ms.com still has "
                         "aliases, delete them first.",
                         command)

    def testdelsrvtarget(self):
        command = ["del", "address", "--fqdn", "arecord15.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "DNS Record arecord15.aqd-unittest.ms.com is still in "
                         "use by SRV records, delete them first.",
                         command)

    def testdelserviceaddress(self):
        ip = self.net["zebra_vip"].usable[1]
        command = ["del", "address", "--fqdn", "zebra2.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "DNS Record zebra2.aqd-unittest.ms.com [%s] is used "
                         "as a service address, therefore it cannot be "
                         "deleted." % ip,
                         command)

    def testdelserveralias(self):
        command = ["del_alias", "--fqdn", "srv-alias2.one-nyp.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Alias srv-alias2.one-nyp.ms.com still provides "
                         "the following services, and cannot be deleted: "
                         "utsvc/utsi2.",
                         command)

    def testdeldynamic(self):
        ip = self.net["dyndhcp0"].usable[2]
        fqdn = self.dynname(ip)
        command = ["del_address", "--ip", ip]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "DNS Record %s [%s] is reserved for dynamic DHCP, "
                         "use del_dynamic_range to delete it." % (fqdn, ip),
                         command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestDnsConstraints)
    unittest.TextTestRunner(verbosity=2).run(suite)
