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
"""Contains the logic for `aq add resourcegroup`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import ResourceGroup, Resource
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.add_resource import CommandAddResource


class CommandAddResourceGroup(CommandAddResource):

    required_parameters = ["resourcegroup"]
    resource_class = ResourceGroup
    resource_name = "resourcegroup"

    def setup_resource(self, session, logger, dbrg, required_type, **_):
        if required_type is not None:
            rqtype = Resource.polymorphic_subclass(required_type,
                                                   "Unknown resource type")
            if rqtype == ResourceGroup:
                raise ArgumentError("A resourcegroup can't hold other "
                                    "resourcegroups.")

            # Normalize the value
            dbrg.required_type = rqtype.__mapper__.polymorphic_identity
