# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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
"""Contains the logic for `aq add application`."""

from aquilon.aqdb.model import Application
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.add_resource import CommandAddResource
from aquilon.worker.dbwrappers.grn import lookup_grn


class CommandAddApplication(CommandAddResource):

    required_parameters = ["application"]
    resource_class = Application
    resource_name = "application"

    def setup_resource(self, session, logger, dbapp, eon_id, grn, **_):
        dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                           config=self.config)
        dbapp.grn = dbgrn
