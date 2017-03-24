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
"""Resource formatter."""

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import Resource


class ResourceFormatter(ObjectFormatter):

    suppress_name = False

    def extra_details(self, share, indent=""):  # pylint: disable=W0613
        return []

    def format_raw(self, resource, indent="", embedded=True,
                   indirect_attrs=True):
        details = []

        if self.suppress_name:
            details.append(indent + format(resource, "c"))
        else:
            details.append(indent + "{0:c}: {0.name}".format(resource))

        if resource.comments:
            details.append(indent + "  Comments: %s" % resource.comments)

        if not embedded:
            details.append(indent + "  Bound to: {0}".format(resource.holder))
        details.extend(self.extra_details(resource, indent))
        return "\n".join(details)

    def fill_proto(self, resource, skeleton, embedded=True,
                   indirect_attrs=True):
        skeleton.name = resource.name
        skeleton.type = resource.resource_type

ObjectFormatter.handlers[Resource] = ResourceFormatter()
