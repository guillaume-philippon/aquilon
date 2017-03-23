# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2016  Contributor
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
"""Contains the logic for `aq add hub`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Organization, Hub
from aquilon.worker.commands import BrokerCommand
from aquilon.worker.dbwrappers.location import add_location


class CommandAddHub(BrokerCommand):

    required_parameters = ["hub"]

    def render(self, session, organization, hub, fullname, comments, **_):
        organization = organization or self.config.get("broker",
                                                       "default_organization")
        if not organization:
            raise ArgumentError("Please specify --organization, since no "
                                "default is available.")

        dborg = Organization.get_unique(session, organization, compel=True)
        add_location(session, Hub, hub, dborg, fullname=fullname,
                     comments=comments)

        session.flush()

        return
