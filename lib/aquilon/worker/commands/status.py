# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2015,2016  Contributor
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
"""Contains the logic for `aq status`."""

from aquilon.aqdb.db_factory import db_prompt
from aquilon.worker.broker import BrokerCommand


class CommandStatus(BrokerCommand):

    requires_readonly = True

    def render(self, session, dbuser, **_):
        stat = []
        stat.append("Aquilon Broker %s" % self.config.get("broker", "version"))
        stat.append("Server: %s" % self.config.get("broker", "servername"))
        stat.append("Database: %s" % db_prompt(session))
        stat.append("Sandboxes: %s" % self.config.get("broker", "templatesdir"))
        if dbuser:
            stat.append("Connected as: %s [%s]" % (dbuser, dbuser.role.name))
        return stat
