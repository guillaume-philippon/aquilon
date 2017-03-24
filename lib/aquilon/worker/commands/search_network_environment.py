# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2016  Contributor
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
"""Contains the logic for `aq search network_environment`."""

from sqlalchemy.orm import joinedload, undefer

from aquilon.aqdb.model import NetworkEnvironment
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.location import get_location
from aquilon.worker.formats.list import StringAttributeList


class CommandSearchNetworkEnvironment(BrokerCommand):

    required_parameters = []

    def render(self, session, network_environment, fullinfo, style,
               **arguments):
        q = session.query(NetworkEnvironment)
        q = q.options(undefer('comments'),
                      joinedload('dns_environment'),
                      undefer('dns_environment.comments'),
                      joinedload('location'))
        if network_environment:
            q = q.filter_by(name=network_environment)
        location = get_location(session, **arguments)
        if location:
            q = q.filter_by(location=location)
        q = q.order_by(NetworkEnvironment.name)

        if fullinfo or style != "raw":
            return q.all()
        else:
            return StringAttributeList(q.all(), "name")
