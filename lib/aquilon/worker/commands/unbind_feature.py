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

from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.bind_feature import CommandBindFeature
from aquilon.aqdb.model import FeatureLink
from aquilon.worker.dbwrappers.parameter import del_all_feature_parameter


class CommandUnBindFeature(CommandBindFeature):

    required_parameters = ['feature']

    def do_link(self, session, logger, dbfeature, params):
        dblink = FeatureLink.get_unique(session, feature=dbfeature, compel=True,
                                        **params)

        # check any params defined for feature in personality and delete them
        del_all_feature_parameter(session, dblink)

        # Ensure all collections are up-to-date in memory, because SQLAlchemy
        # does not automatically remove deleted objects from loaded collections
        if dblink.personality_stage:
            dblink.personality_stage.features.remove(dblink)
        if dblink.archetype:
            dblink.archetype.features.remove(dblink)
        if dblink.model:
            dblink.model.features.remove(dblink)
        dbfeature.links.remove(dblink)

        session.delete(dblink)
