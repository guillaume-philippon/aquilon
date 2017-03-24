#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2012,2013,2014,2015,2016  Contributor
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
"""Module for testing network device discovery."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand
from netdevtest import VerifyNetworkDeviceMixin


class TestDiscoverNetworkDevice(TestBrokerCommand, VerifyNetworkDeviceMixin):

    def test_100_add_swsync(self):
        ip = self.net["switch_sync"].usable[0]
        self.dsdb_expect_add("swsync.aqd-unittest.ms.com", ip,
                             interface="mgmt0", mac=ip.mac)
        self.noouttest(["add", "network_device", "--type", "misc",
                        "--network_device", "swsync.aqd-unittest.ms.com",
                        "--interface", "mgmt0", "--iftype", "physical",
                        "--ip", ip, "--mac", ip.mac,
                        "--rack", "ut3", "--model", "temp_switch"])
        self.dsdb_verify()

    def test_110_add_swsync_ifaces(self):
        self.noouttest(["add", "interface", "--network_device", "swsync",
                        "--interface", "vlan100", "--iftype", "virtual"])
        self.noouttest(["add", "interface", "--network_device", "swsync",
                        "--interface", "vlan200", "--iftype", "virtual"])
        self.noouttest(["add", "interface", "--network_device", "swsync",
                        "--interface", "vlan300", "--iftype", "virtual"])
        self.noouttest(["add", "interface", "--network_device", "swsync",
                        "--interface", "vlan400", "--iftype", "virtual"])

    def test_120_add_swsync_addrs(self):
        ip1 = self.net["switch_sync"].usable[1]
        ip2 = self.net["switch_sync"].usable[2]
        ip3 = self.net["switch_sync"].usable[3]
        self.dsdb_expect_add("swsync-vlan100.aqd-unittest.ms.com",
                             ip1, "vlan100",
                             primary="swsync.aqd-unittest.ms.com")
        self.dsdb_expect_add("swsync-nomatch.aqd-unittest.ms.com",
                             ip2, "vlan200",
                             primary="swsync.aqd-unittest.ms.com")
        self.dsdb_expect_add("swsync-vlan300.aqd-unittest.ms.com",
                             ip3, "vlan300",
                             primary="swsync.aqd-unittest.ms.com")
        self.noouttest(["add", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan100", "--ip", ip1,
                        "--fqdn", "swsync-vlan100.aqd-unittest.ms.com"])
        self.noouttest(["add", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan200", "--ip", ip2,
                        "--fqdn", "swsync-nomatch.aqd-unittest.ms.com"])
        self.noouttest(["add", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan300", "--ip", ip3,
                        "--fqdn", "swsync-vlan300.aqd-unittest.ms.com"])
        self.dsdb_verify()

    def test_200_show(self):
        ip1 = self.net["switch_sync"].usable[1]
        ip2 = self.net["switch_sync"].usable[2]
        ip3 = self.net["switch_sync"].usable[3]
        ip4 = self.net["switch_sync"].usable[4]
        ip5 = self.net["switch_sync"].usable[5]
        command = ["show", "network_device", "--network_device", "swsync", "--discover"]
        out = self.commandtest(command)
        self.matchoutput(out,
                         "aq update_network_device --network_device swsync.aqd-unittest.ms.com "
                         "--model ws-c2960-48tt-l --vendor cisco "
                         "--comments 'T1 T2'",
                         command)
        self.matchoutput(out, "aq del_interface_address "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan100 --ip %s" % ip1, command)
        self.matchoutput(out, "aq del_interface "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan400", command)
        self.matchoutput(out, "aq update_interface "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan200 --rename_to vlan210", command)
        self.matchoutput(out, "aq update_interface "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan300 --rename_to vlan310", command)
        self.matchoutput(out, "aq add_interface_address "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan100 --ip %s --label hsrp" % ip1,
                         command)
        self.matchoutput(out, "aq add_interface_address "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan100 --ip %s" % ip4, command)
        self.matchoutput(out, "aq add_interface "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan500 --iftype virtual", command)
        self.matchoutput(out, "aq add_interface_address "
                         "--network_device swsync.aqd-unittest.ms.com "
                         "--interface vlan500 --ip %s" % ip5, command)
        self.matchoutput(out, "qip-set-router %s" % ip1, command)

    def test_210_update(self):
        ip1 = self.net["switch_sync"].usable[1]
        ip4 = self.net["switch_sync"].usable[4]
        ip5 = self.net["switch_sync"].usable[5]
        self.dsdb_expect_update("swsync.aqd-unittest.ms.com",
                                "mgmt0", comments="T1 T2")
        self.dsdb_expect_update("swsync-vlan100.aqd-unittest.ms.com",
                                "vlan100", ip4, comments="T1 T2")
        self.dsdb_expect_add("swsync-vlan100-hsrp.aqd-unittest.ms.com", ip1,
                             "vlan100_hsrp", comments="T1 T2",
                             primary="swsync.aqd-unittest.ms.com")
        self.dsdb_expect_update("swsync-nomatch.aqd-unittest.ms.com",
                                "vlan200", comments="T1 T2")
        self.dsdb_expect_update("swsync-vlan300.aqd-unittest.ms.com",
                                "vlan300", comments="T1 T2")
        self.dsdb_expect_rename("swsync-nomatch.aqd-unittest.ms.com",
                                iface="vlan200", new_iface="vlan210")
        self.dsdb_expect_rename("swsync-vlan300.aqd-unittest.ms.com",
                                "swsync-vlan310.aqd-unittest.ms.com",
                                "vlan300", "vlan310")
        self.dsdb_expect_add("swsync-vlan500.aqd-unittest.ms.com", ip5,
                             "vlan500", comments="T1 T2",
                             primary="swsync.aqd-unittest.ms.com")
        command = ["update", "network_device", "--network_device", "swsync", "--discover"]
        out, err = self.successtest(command)
        self.matchoutput(err,
                         "Using jump host nyaqd1.ms.com from service instance "
                         "poll_helper/unittest to run discovery for switch "
                         "swsync.aqd-unittest.ms.com.",
                         command)
        self.matchoutput(err, "You should run 'qip-set-router %s'." % ip1,
                         command)
        self.dsdb_verify()

    def test_300_verify(self):
        ip = self.net["switch_sync"].usable[0]
        ip1 = self.net["switch_sync"].usable[1]
        ip2 = self.net["switch_sync"].usable[2]
        ip3 = self.net["switch_sync"].usable[3]
        ip4 = self.net["switch_sync"].usable[4]
        ip5 = self.net["switch_sync"].usable[5]
        out, command = self.verifynetdev("swsync.aqd-unittest.ms.com",
                                         "cisco", "ws-c2960-48tt-l", "ut3", "a",
                                         "3", switch_type="misc",
                                         ip=ip, mac=ip.mac,
                                         interface="mgmt0",
                                         comments="T1 T2")
        # TODO: the interface type is not updated, it's not clear if it should
        self.searchoutput(out,
                          r"Interface: mgmt0 %s\s*"
                          r"Type: physical\s*"
                          r"Network Environment: internal\s*"
                          r"Provides: swsync.aqd-unittest.ms.com \[%s\]"
                          % (ip.mac, ip), command)
        self.searchoutput(out,
                          r"Interface: vlan100 \(no MAC addr\)\s*"
                          r"Type: virtual\s*"
                          r"Network Environment: internal\s*"
                          r"Provides: swsync-vlan100.aqd-unittest.ms.com \[%s\]\s*"
                          r"Provides: swsync-vlan100-hsrp.aqd-unittest.ms.com \[%s\] \(label: hsrp\)"
                          % (ip4, ip1), command)
        self.searchoutput(out,
                          r"Interface: vlan210 \(no MAC addr\)\s*"
                          r"Type: virtual\s*"
                          r"Network Environment: internal\s*"
                          r"Provides: swsync-nomatch.aqd-unittest.ms.com \[%s\]"
                          % ip2, command)
        self.searchoutput(out,
                          r"Interface: vlan310 \(no MAC addr\)\s*"
                          r"Type: virtual\s*"
                          r"Network Environment: internal\s*"
                          r"Provides: swsync-vlan310.aqd-unittest.ms.com \[%s\]"
                          % ip3, command)
        self.searchoutput(out,
                          r"Interface: vlan500 \(no MAC addr\)\s*"
                          r"Type: virtual\s*"
                          r"Network Environment: internal\s*"
                          r"Provides: swsync-vlan500.aqd-unittest.ms.com \[%s\]"
                          % ip5, command)

    def test_400_del_swsync_addrs(self):
        ip1 = self.net["switch_sync"].usable[1]
        ip2 = self.net["switch_sync"].usable[2]
        ip3 = self.net["switch_sync"].usable[3]
        ip4 = self.net["switch_sync"].usable[4]
        ip5 = self.net["switch_sync"].usable[5]
        self.dsdb_expect_delete(ip1)
        self.dsdb_expect_delete(ip2)
        self.dsdb_expect_delete(ip3)
        self.dsdb_expect_delete(ip4)
        self.dsdb_expect_delete(ip5)
        self.noouttest(["del", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan100", "--ip", ip1])
        self.noouttest(["del", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan100", "--ip", ip4])
        self.noouttest(["del", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan210", "--ip", ip2])
        self.noouttest(["del", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan310", "--ip", ip3])
        self.noouttest(["del", "interface", "address", "--network_device", "swsync",
                        "--interface", "vlan500", "--ip", ip5])
        self.dsdb_verify()

    def test_410_del_swsync(self):
        self.dsdb_expect_delete(self.net["switch_sync"].usable[0])
        self.noouttest(["del", "network_device", "--network_device", "swsync"])
        self.dsdb_verify()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDiscoverNetworkDevice)
    unittest.TextTestRunner(verbosity=2).run(suite)
