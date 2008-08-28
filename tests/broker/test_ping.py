#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Module for testing the ping command."""

import os
import sys
import unittest

if __name__ == "__main__":
    BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    SRCDIR = os.path.join(BINDIR, "..", "..")
    sys.path.append(os.path.join(SRCDIR, "lib", "python2.5"))

from brokertest import TestBrokerCommand


class TestPing(TestBrokerCommand):

    def testping(self):
        command = "ping"
        out = self.commandtest(command)
        self.matchoutput(out, "pong", command)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPing)
    unittest.TextTestRunner(verbosity=2).run(suite)
