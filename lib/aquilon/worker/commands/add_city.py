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
"""Contains the logic for `aq add city`."""

from aquilon.aqdb.model import City, Country, Campus
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.location import add_location
from aquilon.worker.processes import DSDBRunner


class CommandAddCity(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["city", "timezone"]

    def render(self, session, logger, plenaries, city, country, fullname, comments,
               timezone, campus, **_):
        if country:
            dbparent = Country.get_unique(session, country, compel=True)
        else:
            dbparent = Campus.get_unique(session, campus, compel=True)

        dbcity = add_location(session, City, city, dbparent, fullname=fullname,
                              comments=comments, timezone=timezone)

        session.flush()

        plenaries.add(dbcity)

        with plenaries.transaction():
            dsdb_runner = DSDBRunner(logger=logger)
            dsdb_runner.add_city(city, dbcity.country.name, fullname)
            dsdb_runner.commit_or_rollback()

        return
