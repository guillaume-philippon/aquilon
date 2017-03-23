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
"""Module for testing the add reboot_schedule command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestAddRebootSchedule(TestBrokerCommand):

    def test_100_nonexistent(self):
        command = ["show_reboot_schedule",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_110_add_schedule(self):
        command = ["add_reboot_schedule",
                   "--week=all", "--day=Sun", "--time=08:00",
                   "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)

    def test_115_make(self):
        command = ["make", "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)

    def test_120_show_reboot_schedule(self):
        command = ["show_reboot_schedule",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out, "RebootSchedule$", command)
        self.matchoutput(out, "Bound to: Host server1.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "Week: All", command)
        self.matchoutput(out, "Day: Sun", command)
        self.matchoutput(out, "Time: 08:00", command)

    def test_120_cat_resource(self):
        command = ["cat", "--reboot_schedule",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         "structure template resource"
                         "/host/server1.aqd-unittest.ms.com"
                         "/reboot_schedule/reboot_schedule/config;",
                         command)
        self.matchoutput(out, "\"name\" = \"reboot_schedule\";", command)
        self.matchoutput(out, "\"time\" = \"08:00\";", command)
        self.matchoutput(out, "\"week\" = \"All\"", command)
        self.matchoutput(out, "\"day\" = \"Sun\"", command)

        command = ["cat", "--reboot_schedule",
                   "--hostname=server1.aqd-unittest.ms.com",
                   "--generate"]
        newout = self.commandtest(command)
        self.assertEqual(out, newout)

    def test_120_cat_host(self):
        command = ["cat", "--hostname", "server1.aqd-unittest.ms.com", "--data"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         '"system/resources/reboot_schedule" = '
                         'append(create("resource/host/server1.aqd-unittest.ms.com/reboot_schedule/reboot_schedule/config"))',
                         command)

    def test_120_show_all(self):
        command = ["show_reboot_schedule", "--all"]
        out = self.commandtest(command)
        self.searchoutput(out, "RebootSchedule$", command)

    def test_120_show_host(self):
        command = ["show_host", "--host=server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out, "RebootSchedule$", command)

    def test_120_show_host_proto(self):
        command = ["show_host", "--hostname=server1.aqd-unittest.ms.com",
                   "--format=proto"]
        host = self.protobuftest(command, expect=1)[0]
        found = False
        for resource in host.resources:
            if resource.name == "reboot_schedule" and \
               resource.type == "reboot_schedule":
                found = True
                self.assertEqual(resource.reboot_schedule.week, "All")
                self.assertEqual(resource.reboot_schedule.day, "Sun")
                self.assertEqual(resource.reboot_schedule.time, "08:00")
        self.assertTrue(found,
                        "Reboot schedule not found in the resources. "
                        "Existing resources: %s" %
                        ", ".join("%s %s" % (res.type, res.name)
                                  for res in host.resources))

    def test_130_add_schedule_no_time(self):
        command = ["add_reboot_schedule", "--week=1,3", "--day=Sat",
                   "--hostname=server2.aqd-unittest.ms.com"]
        self.successtest(command)

    def test_131_make_server2(self):
        command = ["make", "--hostname=server1.aqd-unittest.ms.com"]
        self.successtest(command)

    def test_135_show_server2_reboot_schedule(self):
        command = ["show_reboot_schedule",
                   "--hostname=server2.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.searchoutput(out, "RebootSchedule$", command)
        self.matchoutput(out, "Bound to: Host server2.aqd-unittest.ms.com",
                         command)
        self.matchoutput(out, "Week: 1,3", command)
        self.matchoutput(out, "Day: Sat", command)
        self.matchoutput(out, "Time: None", command)

    def test_135_cat_resource(self):
        command = ["cat", "--reboot_schedule",
                   "--hostname=server2.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         "structure template resource"
                         "/host/server2.aqd-unittest.ms.com"
                         "/reboot_schedule/reboot_schedule/config;",
                         command)
        self.matchoutput(out, "\"name\" = \"reboot_schedule\";", command)
        self.matchoutput(out, "\"time\" = null;", command)
        self.matchoutput(out, "\"week\" = \"1,3\"", command)
        self.matchoutput(out, "\"day\" = \"Sat\"", command)

    def test_135_show_server2_proto(self):
        command = ["show_host", "--hostname=server2.aqd-unittest.ms.com",
                   "--format=proto"]
        host = self.protobuftest(command, expect=1)[0]
        found = False
        for resource in host.resources:
            if resource.name == "reboot_schedule" and \
               resource.type == "reboot_schedule":
                found = True
                self.assertEqual(resource.reboot_schedule.week, "1,3")
                self.assertEqual(resource.reboot_schedule.day, "Sat")
                self.assertEqual(resource.reboot_schedule.time, "")
        self.assertTrue(found,
                        "Reboot schedule not found in the resources. "
                        "Existing resources: %s" %
                        ", ".join("%s %s" % (res.type, res.name)
                                  for res in host.resources))

    def test_200_add_existing(self):
        command = ["add_reboot_schedule",
                   "--week=all", "--day=Sun", "--time=08:00",
                   "--hostname=server1.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "already exists", command)

    def test_200_cat_notfound(self):
        command = ["cat", "--reboot_schedule",
                   "--hostname=server3.aqd-unittest.ms.com"]
        self.notfoundtest(command)

    def test_210_add_schedule_fail(self):
        command = ["add_reboot_schedule",
                   "--week=all", "--day=Sun", "--time=200",
                   "--hostname=server3.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Key 'time' contains an invalid value.", command)

    def test_220_add_schedule_fail(self):
        command = ["add_reboot_schedule",
                   "--week=all", "--day=Sun", "--time=25:00",
                   "--hostname=server3.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "The preferred time '25:00' could not be interpreted: hour must be in 0..23", command)

    def test_230_add_schedule_fail(self):
        command = ["add_reboot_schedule",
                   "--week=all", "--day=Sun", "--time=08:61",
                   "--hostname=server3.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "The preferred time '08:61' could not be interpreted: minute must be in 0..59", command)

    def test_240_add_schedule_fail(self):
        command = ["add_reboot_schedule",
                   "--week=1,3,5", "--day=Sun", "--time=08:00",
                   "--hostname=server3.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Key 'week' contains an invalid value. Valid values are (1|2|3|4|all).", command)

    def test_250_add_schedule_fail(self):
        command = ["add_reboot_schedule",
                   "--week=5", "--day=Sun", "--time=08:00",
                   "--hostname=server3.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Key 'week' contains an invalid value. Valid values are (1|2|3|4|all).", command)

    def test_260_add_schedule_fail(self):
        command = ["add_reboot_schedule",
                   "--week=all", "--day=foo", "--time=08:00",
                   "--hostname=server3.aqd-unittest.ms.com"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Key 'day' contains an invalid value. Valid values are (Sun|Mon|Tue|Wed|Thu|Fri|Sat).", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddRebootSchedule)
    unittest.TextTestRunner(verbosity=2).run(suite)
