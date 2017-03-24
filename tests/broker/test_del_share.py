#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2012,2013,2014,2015,2016  Contributor
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
"""Module for testing the add service command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestDelShare(TestBrokerCommand):

    def testdel10gigshares(self):
        for i in range(5, 11):
            self.noouttest(["del_share", "--cluster=utecl%d" % i,
                            "--share=utecl%d_share" % i])

    def testdelnasshares(self):
        for i in range(1, 9):
            self.noouttest(["del_share", "--cluster=utecl1",
                            "--share=test_share_%s" % i])

        self.noouttest(["del_share", "--cluster=utecl2",
                        "--share=test_share_1"])

    def testdelutmc8shares(self):
        command = ["del_share", "--resourcegroup=utmc8as1",
                   "--metacluster=utmc8", "--share=test_v2_share"]
        self.noouttest(command)
        command = ["del_share", "--resourcegroup=utmc8as2",
                   "--metacluster=utmc8", "--share=test_v2_share"]
        self.noouttest(command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelShare)
    unittest.TextTestRunner(verbosity=2).run(suite)
