#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2014,2015,2016  Contributor
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
"""Module for testing the refresh user principals command."""

import os
import pwd

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestRefreshUser(TestBrokerCommand):
    def test_000_patch_userlist(self):
        dst_filename = self.config.get("broker", "user_list_location")
        src_filename = dst_filename + ".in"
        with open(src_filename, "r") as f:
            lines = f.readlines()

        # Make sure the current user is always there
        pwrec = pwd.getpwuid(os.getuid())
        lines.insert(0, "%s\t%s:dontcare:1000:1000:Current user:%s:%s\n" %
                     (self.user, pwrec[0], pwrec[5], pwrec[6]))

        with open(dst_filename, "w") as f:
            f.writelines(lines)

    def test_110_grant_testuser4_root(self):
        command = ["grant_root_access", "--user", "testuser4",
                   "--personality", "utunused/dev", "--justification", "tcm=12345678"]
        self.successtest(command)

    def test_111_verify_testuser4_root(self):
        command = ["show_personality", "--personality", "utunused/dev"]
        out = self.commandtest(command)
        self.matchoutput(out, "Root Access User: testuser4", command)

        command = ["cat", "--personality", "utunused/dev",
                   "--archetype", "aquilon"]
        out = self.commandtest(command)
        self.matchoutput(out, "testuser4", command)

    def test_200_refresh(self):
        command = ["refresh", "user"]
        err = self.statustest(command)
        self.matchoutput(err,
                         "Duplicate UID: 1236 is already used by testuser3, "
                         "skipping dup_uid.",
                         command)
        self.matchoutput(err, "Added 2, deleted 1, updated 1 users.", command)

    def test_210_verify_all(self):
        command = ["show_user", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, "testuser1", command)
        self.matchoutput(out, "testuser2", command)
        self.matchoutput(out, "testuser3", command)
        self.matchclean(out, "testuser4", command)
        self.matchclean(out, "bad_line", command)
        self.matchclean(out, "dup_uid", command)

    def test_210_verify_testuser1(self):
        command = ["show_user", "--username", "testuser1"]
        out = self.commandtest(command)
        self.searchoutput(out, r'User: testuser1$', command)
        self.searchoutput(out, r'UID: 1234$', command)
        self.searchoutput(out, r'GID: 423$', command)
        self.searchoutput(out, r'Full Name: test user 1$', command)
        self.searchoutput(out, r'Home Directory: /tmp$', command)

    def test_210_verify_testuser3(self):
        command = ["show_user", "--username", "testuser3"]
        out = self.commandtest(command)
        self.searchoutput(out, r'User: testuser3$', command)
        self.searchoutput(out, r'UID: 1236$', command)
        self.searchoutput(out, r'GID: 655$', command)
        self.searchoutput(out, r'Full Name: test user 3$', command)
        self.searchoutput(out, r'Home Directory: /tmp/foo$', command)

    def test_220_verify_testuser4_root_gone(self):
        command = ["show_personality", "--personality", "utunused/dev"]
        out = self.commandtest(command)
        self.matchclean(out, "testuser4", command)

        command = ["cat", "--personality", "utunused/dev",
                   "--archetype", "aquilon"]
        out = self.commandtest(command)
        self.matchclean(out, "testuser4", command)

    def test_300_update_testuser3(self):
        self.noouttest(["update_user", "--username", "testuser3",
                        "--uid", "1237", "--gid", "123",
                        "--full_name", "Some other name",
                        "--home_directory", "/tmp"])

    def test_301_verify_testuser3_before_sync(self):
        command = ["show_user", "--username", "testuser3"]
        out = self.commandtest(command)
        self.searchoutput(out, r'User: testuser3$', command)
        self.searchoutput(out, r'UID: 1237$', command)
        self.searchoutput(out, r'GID: 123$', command)
        self.searchoutput(out, r'Full Name: Some other name$', command)
        self.searchoutput(out, r'Home Directory: /tmp$', command)

    def test_305_refresh_again(self):
        command = ["refresh", "user", "--incremental"]
        err = self.partialerrortest(command)
        self.matchoutput(err,
                         "Duplicate UID: 1236 is already used by testuser3, "
                         "skipping dup_uid.",
                         command)
        self.matchoutput(err,
                         "Updating user testuser3 (uid = 1236, was 1237; "
                         "gid = 655, was 123; "
                         "full_name = test user 3, was Some other name; "
                         "home_dir = /tmp/foo, was /tmp)",
                         command)

    def test_310_verify_testuser1_again(self):
        command = ["show_user", "--username", "testuser1"]
        out = self.commandtest(command)
        self.searchoutput(out, r'User: testuser1$', command)
        self.searchoutput(out, r'UID: 1234$', command)
        self.searchoutput(out, r'GID: 423$', command)
        self.searchoutput(out, r'Full Name: test user 1$', command)
        self.searchoutput(out, r'Home Directory: /tmp$', command)

    def test_310_verify_testuser3_again(self):
        command = ["show_user", "--username", "testuser3"]
        out = self.commandtest(command)
        self.searchoutput(out, r'User: testuser3$', command)
        self.searchoutput(out, r'UID: 1236$', command)
        self.searchoutput(out, r'GID: 655$', command)
        self.searchoutput(out, r'Full Name: test user 3$', command)
        self.searchoutput(out, r'Home Directory: /tmp/foo$', command)

    def test_310_verify_all_again(self):
        command = ["show_user", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, "testuser1", command)
        self.matchoutput(out, "testuser2", command)
        self.matchoutput(out, "testuser3", command)
        self.matchclean(out, "testuser4", command)
        self.matchclean(out, "bad_line", command)
        self.matchclean(out, "dup_uid", command)

    def test_320_add_users(self):
        limit = self.config.getint("broker", "user_delete_limit")
        for i in range(limit + 5):
            name = "testdel_%d" % i
            uid = i + 5000
            self.noouttest(["add_user", "--username", name, "--uid", uid,
                            "--gid", 1000, "--full_name", "Delete test",
                            "--home_directory", "/tmp"])

    def test_321_refresh_refuse(self):
        limit = self.config.getint("broker", "user_delete_limit")
        command = ["refresh", "user"]
        out = self.statustest(command)
        self.matchoutput(out,
                         "Cowardly refusing to delete %s users, because "
                         "it's over the limit of %s.  Use the "
                         "--ignore_delete_limit option to override." %
                         (limit + 5, limit),
                         command)
        self.matchoutput(out, "deleted 0,", command)

    def test_322_verify_still_there(self):
        command = ["show_user", "--all"]
        out = self.commandtest(command)
        limit = self.config.getint("broker", "user_delete_limit")
        for i in range(limit + 5):
            name = "testdel_%d" % i
            self.matchoutput(out, name, command)

    def test_323_refresh_override(self):
        limit = self.config.getint("broker", "user_delete_limit")
        command = ["refresh", "user", "--ignore_delete_limit"]
        out = self.statustest(command)
        self.matchoutput(out,
                         "Added 0, deleted %s, updated 0 users." % (limit + 5),
                         command)

    def test_324_verify_all_gone(self):
        command = ["show_user", "--all"]
        out = self.commandtest(command)
        self.matchoutput(out, "testuser1", command)
        self.matchoutput(out, "testuser2", command)
        self.matchoutput(out, "testuser3", command)
        self.matchclean(out, "testuser4", command)
        self.matchclean(out, "bad_line", command)
        self.matchclean(out, "dup_uid", command)
        self.matchclean(out, "testdel_", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRefreshUser)
    unittest.TextTestRunner(verbosity=2).run(suite)
