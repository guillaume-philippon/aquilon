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
"""Contains the logic for `aq show feature --all`."""

from sqlalchemy.orm import undefer, subqueryload

from aquilon.worker.broker import BrokerCommand
from aquilon.aqdb.model import Feature


class CommandShowFeatureAll(BrokerCommand):

    required_parameters = []

    def render(self, session, **_):
        q = session.query(Feature)
        q = q.options(undefer(Feature.comments),
                      subqueryload('owner_grn'),
                      subqueryload('links'),
                      subqueryload('links.archetype'),
                      subqueryload('links.personality_stage'),
                      subqueryload('links.model'))
        q = q.order_by(Feature.feature_type, Feature.post_personality,
                       Feature.name)
        return q.all()
