# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2016  Contributor
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
""" Contains the logic for `aq update cluster autostartlist`. """

from aquilon.exceptions_ import NotFoundException
from aquilon.aqdb.model import AutoStartList
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.update_resource import CommandUpdateResource
from aquilon.worker.dbwrappers.host import hostname_to_host


class CommandUpdateClusterAutoStartList(CommandUpdateResource):

    required_parameters = ["cluster"]
    resource_class = AutoStartList

    def update_resource(self, dbresource, session, logger, member, order, **_):
        if member is not None:
            dbhost = hostname_to_host(session, member)
            try:
                entry = dbresource.entries[dbhost]
            except KeyError:
                raise NotFoundException("{0} does not have an AutoStartList entry."
                                        .format(dbhost))
            if order is not None:
                entry.priority = order

    def render(self, **kwargs):
        super(CommandUpdateClusterAutoStartList, self).render(hostname=None,
                                                              metacluster=None,
                                                              comments=None,
                                                              **kwargs)
