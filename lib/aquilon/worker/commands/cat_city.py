# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2015,2016  Contributor
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
"""Contains the logic for `aq cat --city`."""

from aquilon.aqdb.model import City
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.templates import Plenary


class CommandCatCity(BrokerCommand):

    required_parameters = ["city"]

    # We do not lock the plenary while reading it
    _is_lock_free = True

    def render(self, generate, session, logger, city, **_):
        dbcity = City.get_unique(session, city, compel=True)
        plenary_info = Plenary.get_plenary(dbcity, logger=logger)

        if generate:
            return plenary_info._generate_content()
        else:
            return plenary_info.read()
