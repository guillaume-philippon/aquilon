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
"""Contains the logic for `aq show personality`."""

from sqlalchemy.orm import joinedload, subqueryload, contains_eager

from aquilon.aqdb.model import Archetype, Personality, PersonalityStage
from aquilon.worker.broker import BrokerCommand


class CommandShowPersonality(BrokerCommand):

    required_parameters = []

    def render(self, session, personality, archetype, **arguments):
        if archetype:
            dbarchetype = Archetype.get_unique(session, archetype, compel=True)
        else:
            dbarchetype = None

        if archetype and personality:
            dbpersonality = Personality.get_unique(session, name=personality,
                                                   archetype=dbarchetype,
                                                   compel=True)
            return dbpersonality.default_stage

        q = session.query(PersonalityStage)
        q = q.join(Personality)
        if archetype:
            q = q.filter_by(archetype=dbarchetype)
        if personality:
            q = q.filter_by(name=personality)
        q = q.join(Archetype)
        q = q.order_by(Archetype.name, Personality.name)
        q = q.options(contains_eager('personality'),
                      contains_eager('personality.archetype'),
                      # FIXME: Undo when required services are staged
                      subqueryload('personality.services'),
                      # FIXME: Undo when GRNs are staged
                      subqueryload('personality.grns'),
                      # FIXME: Undo when feature bindings are staged
                      subqueryload('personality.features'),
                      joinedload('personality.features.feature'),
                      # FIXME: Undo when cluster_infos is staged
                      joinedload('personality.cluster_infos'),
                      subqueryload('personality.root_users'),
                      subqueryload('personality.root_netgroups'))

        return q.all()
