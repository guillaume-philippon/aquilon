# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017  Contributor
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
"""Contains the logic for `aq cat --hostname`."""

from aquilon.aqdb.model import ResourceGroup
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.host import hostname_to_host
from aquilon.worker.dbwrappers.resources import get_resource
from aquilon.worker.templates import (Plenary, PlenaryHostObject,
                                      PlenaryHostData, PlenaryResource)


class CommandCatHostname(BrokerCommand):

    required_parameters = ["hostname"]

    # We do not lock the plenary while reading it
    _is_lock_free = True

    def render(self, session, logger, hostname, data, generate, **arguments):
        dbhost = hostname_to_host(session, hostname)
        dbresource = get_resource(session, dbhost, **arguments)
        if dbresource:
            if isinstance(dbresource, ResourceGroup):
                cls = PlenaryResource
            else:
                cls = Plenary
            plenary_info = cls.get_plenary(dbresource, logger=logger)
        else:
            if data:
                cls = PlenaryHostData
            else:
                cls = PlenaryHostObject

            plenary_info = cls.get_plenary(dbhost, logger=logger)

        if generate:
            return plenary_info._generate_content()
        else:
            return plenary_info.read()
