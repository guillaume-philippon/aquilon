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

from aquilon.worker.broker import BrokerCommand
from aquilon.aqdb.model import Feature
from aquilon.worker.dbwrappers.grn import lookup_grn


class CommandUpdateFeature(BrokerCommand):

    def render(self, session, logger, feature, type, comments, grn, eon_id,
               visibility, activation, deactivation, **_):

        cls = Feature.polymorphic_subclass(type, "Unknown feature type")
        dbfeature = cls.get_unique(session, name=feature, compel=True)

        if visibility:
            dbfeature.visibility = visibility

        if grn or eon_id:
            dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                               config=self.config)
            dbfeature.owner_grn = dbgrn

        if comments is not None:
            dbfeature.comments = comments

        if activation:
            dbfeature.activation = activation

        if deactivation:
            dbfeature.deactivation = deactivation

        session.flush()

        return
