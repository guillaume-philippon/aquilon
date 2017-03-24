# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2016  Contributor
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
"""Contains the logic for `aq manage --cluster`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Cluster, MetaCluster
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.manage_list import CommandManageList


class CommandManageCluster(CommandManageList):

    required_parameters = ["cluster"]

    def get_objects(self, session, logger, cluster, **_):
        dbcluster = Cluster.get_unique(session, cluster, compel=True)
        if isinstance(dbcluster, MetaCluster):
            logger.client_info("Please use the --metacluster option for "
                               "managing metaclusters.")
        if dbcluster.metacluster:
            raise ArgumentError("{0.name} is member of metacluster {1.name}, "
                                "it must be managed at metacluster level.".
                                format(dbcluster, dbcluster.metacluster))

        return (dbcluster.branch, dbcluster.sandbox_author,
                list(dbcluster.all_objects()))
