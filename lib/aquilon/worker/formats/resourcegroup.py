# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014  Contributor
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
"""ResourceGroup Resource formatter."""

from operator import attrgetter

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.resource import ResourceFormatter
from aquilon.aqdb.model import ResourceGroup


class ResourceGroupFormatter(ResourceFormatter):
    def extra_details(self, rg, indent=""):
        details = []
        if rg.required_type:
            details.append(indent + "  Type: %s" % rg.required_type)

        if rg.resholder:
            for resource in sorted(rg.resholder.resources,
                                   key=attrgetter('resource_type', 'name')):
                details.append(self.redirect_raw(resource, indent + "  "))

        return details

    def fill_proto(self, rg, skeleton, embedded=True, indirect_attrs=True):
        super(ResourceGroupFormatter, self).fill_proto(rg, skeleton)
        if rg.required_type:
            skeleton.resourcegroup.required_type = rg.required_type

        if rg.resholder:
            self.redirect_proto(rg.resholder.resources,
                                skeleton.resourcegroup.resources)

ObjectFormatter.handlers[ResourceGroup] = ResourceGroupFormatter()
