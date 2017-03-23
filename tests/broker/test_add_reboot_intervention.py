#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013,2014,2015,2016  Contributor
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
"""Module for testing the add reboot_intervention command."""

from datetime import datetime, timedelta
import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand

EXPIRY = datetime.utcnow().replace(microsecond=0) + timedelta(days=1)
EXPIRY = EXPIRY.isoformat().replace("T", " ")


class TestAddRebootIntervention(TestBrokerCommand):

    def test_00_basic_reboot_intervention(self):
        command = ["show_reboot_intervention",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.notfoundtest(command)

        command = ["add_reboot_intervention", "--expiry", EXPIRY,
                   "--reason=test",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)

        command = ["show_reboot_intervention",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out, "RebootIntervention$", command)
        self.matchoutput(out, "Bound to: Host server1.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "Start: ", command)
        self.matchoutput(out, "Expiry: ", command)

        command = ["cat", "--reboot_intervention",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         "structure template resource"
                         "/host/server1.aqd-unittest.ms.com"
                         "/reboot_iv/reboot_intervention/config;",
                         command)
        self.matchoutput(out, "\"name\" = \"reboot_intervention\";", command)
        self.matchoutput(out, "\"start\" =", command)
        self.matchoutput(out, "\"expiry\" =", command)

        command = ["cat", "--reboot_intervention",
                   "--hostname=server1.aqd-unittest.ms.com",
                   "--generate"]
        newout = self.commandtest(command)
        self.assertEqual(out, newout)

        command = ["show_reboot_intervention", "--all"]
        out = self.commandtest(command)
        self.searchoutput(out, "RebootIntervention$", command)

    def test_11_addexisting(self):
        EXPIRY = datetime.utcnow().replace(microsecond=0) + timedelta(days=2)
        command = ["add_reboot_intervention", "--expiry", EXPIRY,
                   "--reason=test",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "already exists", command)

    def test_12_addbadtime(self):
        command = ["add_reboot_intervention", "--start_time=2013/01/01",
                   "--expiry=2013/01/14",
                   "--reason=test",
                   "--hostname=server2.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "The start time or expiry time are in the past.", command)

    def test_15_notfoundri(self):
        command = ["cat", "--reboot_intervention",
                   "--hostname=server3.aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_30_checkthehost(self):
        command = ["show_host", "--host=server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, "RebootIntervention", command)

        command = ["make", "--hostname=server1.aqd-unittest.ms.com"]
        out = self.successtest(command)

        command = ["cat", "--generate",
                   "--hostname", "server1.aqd-unittest.ms.com", "--data"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         '"system/resources/reboot_iv" = '
                         'append(create("resource/host/server1.aqd-unittest.ms.com/reboot_iv/reboot_intervention/config"))',
                         command)

        command = ["show_host", "--hostname=server1.aqd-unittest.ms.com",
                   "--format=proto"]
        host = self.protobuftest(command, expect=1)[0]
        found = False
        for resource in host.resources:
            if resource.name == "reboot_intervention" and \
               resource.type == "reboot_iv":
                found = True
        self.assertTrue(found, "No reboot_iv found in host protobuf.")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestAddRebootIntervention)
    unittest.TextTestRunner(verbosity=2).run(suite)
