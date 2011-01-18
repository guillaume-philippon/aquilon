#!/usr/bin/env python2.6
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2008,2009,2010  Contributor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the EU DataGrid Software License.  You should
# have received a copy of the license with this program, and the
# license is published at
# http://eu-datagrid.web.cern.ch/eu-datagrid/license.html.
#
# THE FOLLOWING DISCLAIMER APPLIES TO ALL SOFTWARE CODE AND OTHER
# MATERIALS CONTRIBUTED IN CONNECTION WITH THIS PROGRAM.
#
# THIS SOFTWARE IS LICENSED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE AND ANY WARRANTY OF NON-INFRINGEMENT, ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. THIS
# SOFTWARE MAY BE REDISTRIBUTED TO OTHERS ONLY BY EFFECTIVELY USING
# THIS OR ANOTHER EQUIVALENT DISCLAIMER AS WELL AS ANY OTHER LICENSE
# TERMS THAT MAY APPLY.
""" Module for testing the search_audit command """
import unittest
from datetime import datetime

if __name__ == "__main__":
    import utils
    utils.import_depends()

from aquilon.server import depends  # pylint: disable=W0611 (for dateutil)
from dateutil.parser import parse

from broker.brokertest import TestBrokerCommand



class TestAudit(TestBrokerCommand):
    """ Test the search_audit features """

    def test_100_get_start(self):
        """ get the oldest row in the xtn table"""
        cmd = ["search_audit", "--cmd", "all", "--limit", "1" ,"--oldest_first"]
        out = self.commandtest(cmd)
        global start_time
        start_time = parse(' '.join(out.split()[0:2]))
        assert isinstance(start_time, datetime)

    def test_101_get_end(self):
        """ get the newest row of xtn table, calcluate midpoint """
        global end_time, midpoint, elapsed

        cmd = ["search_audit", "--cmd", "all", "--limit", "1"]
        out = self.commandtest(cmd)
        global end_time
        end_time = parse(' '.join(out.split()[0:2]))
        assert isinstance(end_time, datetime)
        assert end_time > start_time
        elapsed = end_time - start_time
        global midpoint
        midpoint = start_time + (elapsed / 2)
        assert isinstance(midpoint, datetime)

    def test_200_keyword(self):
        """ test activity on building 'ut' took place """
        cmd = ["search_audit", "--keyword", "ut"]
        out = self.commandtest(cmd)
        self.searchoutput(out, self.user, cmd)

    def test_210_user(self):
        """ test search audit by user name """
        cmd = ["search_audit", "--username", self.user]
        out = self.commandtest(cmd)
        self.searchoutput(out, "--role='engineering'", cmd)

    def test_220_cmd_protobuf(self):
        """ test search audit by command with protobuf output """
        cmd = ["search_audit", "--username", self.user,
               "--cmd", "search_audit", "--format", "proto"]
        out = self.commandtest(cmd)
        outlist = self.parse_audit_msg(out)
        unit = outlist.transactions[0]
        user = self.user + "@is1.morgan"
        self.assertEqual(unit.username, user)
        self.assertEqual(unit.is_readonly, True)

    def test_300_before(self):
        """ test audit 'before' functionality """
        cmd = ["search_audit", "--before", midpoint]
        self.ignoreoutputtest(cmd)

    def test_310_after(self):
        """ test audit 'after' functionality """
        cmd = ["search_audit", "--after", midpoint]
        self.ignoreoutputtest(cmd)

    def test_320_before_and_after(self):
        """ test audit 'before' and 'after' simultaneously """
        cmd = ["search_audit", "--before", end_time,
               "--after", midpoint]
        self.ignoreoutputtest(cmd)

    def test_500_by_return_code(self):
        """ test search by return code """
        cmd = ["search_audit", "--cmd", "add_switch", "--return_code", "200"]
        out = self.commandtest(cmd)
        self.searchoutput(out, "200 aq add_switch", cmd)

    def test_600_rw_command(self):
        """ test the rw option contains read commands and NOT search_audit """
        cmd = ["search_audit", "--cmd", "rw"]
        out = self.commandtest(cmd)
        # test what's there and what's NOT there: make sure audit is not
        self.searchoutput(out, "200 aq show_building", cmd)
        self.searchclean(out, "200 aq search_audit", cmd)

    def test_620_all_command(self):
        """ test the all option """
        cmd = ["search_audit", "--cmd", "all"]
        out = self.commandtest(cmd)
        # test search_audit is there
        self.searchoutput(out, "200 aq search_audit", cmd)

    def test_630_default_no_readonly(self):
        """ test default of writeable commands only """
        cmd = ["search_audit", "--username", self.user]
        out = self.commandtest(cmd)
        self.searchclean(out, "200 aq show_building", cmd)

    def test_700_invalid_before(self):
        """ test invalid date spec in before """
        cmd = ["search_audit", "--cmd", "all", "--before", "today"]
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Unable to parse date string", cmd)

    def test_710_invalid_after(self):
        """ test invalid date spec in after """
        cmd = ["search_audit", "--cmd", "all", "--after", "yesterday"]
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Unable to parse date string", cmd)

    def test_800_limit(self):
        """ test the limit option """
        # use protobufs to exploit the "expect" functionality to count the
        # number of replies
        cmd = ["search_audit", "--cmd", "all", "--limit", 1000, "--format",
               "proto"]
        out = self.commandtest(cmd)
        outlist = self.parse_audit_msg(out, 1000)

    def test_810_max_limit(self):
        """ test the maximum is checked properly """
        cmd = ["search_audit", "--cmd", "all", "--limit", 30000, "--format",
               "proto"]
        out = self.badrequesttest(cmd)
        self.matchoutput(out, "Cannot set the limit higher than", cmd)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAudit)
    unittest.TextTestRunner(verbosity=2).run(suite)
