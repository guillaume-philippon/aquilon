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
"""Module for testing the show service --all command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestShowServiceAll(TestBrokerCommand):

    def testshowserviceall(self):
        command = "show service --all"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Service: afs Instance: q.ny.ms.com", command)
        self.matchoutput(out, "Service: afs Instance: q.ln.ms.com", command)
        self.matchoutput(out, "Service: bootserver Instance: one-nyp", command)
        self.matchoutput(out, "Service: dns Instance: unittest", command)
        self.matchoutput(out, "Service: ntp Instance: pa.ny.na", command)

    def testshowserviceproto(self):
        command = "show service --all --format proto"
        self.protobuftest(command.split(" "))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestShowServiceAll)
    unittest.TextTestRunner(verbosity=2).run(suite)
