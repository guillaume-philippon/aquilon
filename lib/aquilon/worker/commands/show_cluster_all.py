# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2016  Contributor
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
"""Contains the logic for `aq show city --all`."""

from aquilon.aqdb.model import Cluster
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.formats.list import StringAttributeList


class CommandShowClusterAll(BrokerCommand):

    query_class = Cluster

    def render(self, session, **_):
        q = session.query(self.query_class.name).order_by(self.query_class.name)
        if self.query_class == Cluster:
            q = q.filter(Cluster.cluster_type != 'meta')
        return StringAttributeList(q.all(), "name")
