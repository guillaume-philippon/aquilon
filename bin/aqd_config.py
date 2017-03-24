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
"""
Parse AQD configuration
"""

from __future__ import print_function

import argparse
import sys
import os

try:
    import ms.version
except ImportError:
    pass
else:
    ms.version.addpkg('six', '1.7.3')

# -- begin path_setup --
BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
LIBDIR = os.path.join(BINDIR, "..", "lib")

if LIBDIR not in sys.path:
    sys.path.append(LIBDIR)
# -- end path_setup --

from six.moves.configparser import NoSectionError, NoOptionError  # pylint: disable=F0401

from aquilon.config import Config


def list_all(config):
    defaults = {}
    for name, value in config.items("DEFAULT"):
        defaults[name] = value

    for name in sorted(defaults):
        value = config.get("DEFAULT", name)
        print("DEFAULT.%s=%s" % (name, value))

    for section in sorted(config.sections()):
        for name in sorted(config.options(section)):
            value = config.get(section, name)

            # Defaults are copied into every section. Skip them unless the
            # value has been overridden
            if name in defaults and value == defaults[name]:
                continue

            # Skip section inclusion directive
            if name == "%s_section" % section:
                continue

            print("%s.%s=%s" % (section, name, value))


def get_option(config, key):
    if "." not in key:
        raise SystemExit("The key must have the syntax SECTION.OPTION.")
    section, name = key.split('.', 1)
    try:
        print(config.get(section, name))
    except NoSectionError:
        raise SystemExit("No such section: %s" % section)
    except NoOptionError:
        raise SystemExit("No such option in section %s: %s" % (section, name))


def main():
    parser = argparse.ArgumentParser(description="Parse AQD configuration")
    parser.add_argument("-c", "--config", dest="config", action="store",
                        help="parse the given config file instead of the default")
    parser.add_argument("--get", metavar="SECTION.NAME", action="store",
                        help="get the value of the specified configuration key")
    parser.add_argument("--list", action="store_true",
                        help="list all defined configuration options and their values")

    opts = parser.parse_args()

    config = Config(configfile=opts.config)

    if opts.get:
        get_option(config, opts.get)
    elif opts.list:
        list_all(config)
    else:
        raise SystemExit("Please specify an action.")


if __name__ == "__main__":
    main()
