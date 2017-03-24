#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015  Contributor
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
"""Produce schema graphs."""

import os
import sys

# -- begin path_setup --
BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
LIBDIR = os.path.join(BINDIR, "..", "lib")

if LIBDIR not in sys.path:
    sys.path.append(LIBDIR)
# -- end path_setup --

import aquilon.aqdb.depends
from aquilon.config import Config, lookup_file_path

import argparse
parser = argparse.ArgumentParser(description='generate schema graphs')
parser.add_argument('--outputdir', '-o', dest='dir', default='.',
                    help='directory to put generated files')
parser.add_argument('--prefix', '-p', dest='prefix', default='aqdb_schema',
                    help='basename of files to generate')
opts = parser.parse_args()

if not os.path.exists(opts.dir):
    os.makedirs(opts.dir)

config = Config(configfile=lookup_file_path('aqd.conf.mem'))

from aquilon.aqdb.db_factory import DbFactory
from aquilon.aqdb.model import Base
db = DbFactory()
Base.metadata.bind = db.engine
Base.metadata.create_all()

from aquilon.aqdb.utils import schema2dot


dot = schema2dot.create_schema_graph(metadata=Base.metadata)
dot.write(os.path.join(opts.dir, "%s.dot" % opts.prefix))
dot.write_png(os.path.join(opts.dir, "%s.png" % opts.prefix))
