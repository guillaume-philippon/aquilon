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
"""Location formatter."""

from aquilon.aqdb.model import Location, Rack, Building
from aquilon.worker.formats.formatters import ObjectFormatter


class LocationFormatter(ObjectFormatter):
    def format_raw(self, location, indent="", embedded=True,
                   indirect_attrs=True):
        details = [indent + "{0:c}: {0.name}".format(location)]
        if location.fullname:
            details.append(indent + "  Fullname: %s" % location.fullname)
        if hasattr(location, 'timezone'):
            details.append(indent + "  Timezone: %s" % location.timezone)
        # Rack could have been a separate formatter, but since this is
        # the only difference...
        if isinstance(location, Rack):
            details.append(indent + "  Row: %s" % location.rack_row)
            details.append(indent + "  Column: %s" % location.rack_column)
        elif isinstance(location, Building):
            details.append(indent + "  Address: %s" % location.address)
        if location.comments:
            details.append(indent + "  Comments: %s" % location.comments)
        if location.parents:
            details.append(indent + "  Location Parents: [%s]" %
                           ", ".join(format(p) for p in location.parents))
        if location.default_dns_domain:
            details.append(indent + "  Default DNS Domain: %s" %
                           location.default_dns_domain)
        return "\n".join(details)

    def fill_proto(self, loc, skeleton, embedded=True, indirect_attrs=True):
        skeleton.name = loc.name
        # Backwards compatibility
        if loc.location_type == "organization":
            skeleton.location_type = "company"
        else:
            skeleton.location_type = loc.location_type
        skeleton.fullname = loc.fullname
        if isinstance(loc, Rack) and loc.rack_row and loc.rack_column:
            skeleton.row = loc.rack_row
            skeleton.col = loc.rack_column
        if hasattr(loc, "timezone"):
            skeleton.timezone = loc.timezone

        if indirect_attrs:
            for p in loc.parents:
                parent = skeleton.parents.add()
                parent.name = p.name
                # Backwards compatibility
                if p.location_type == "organization":
                    parent.location_type = "company"
                else:
                    parent.location_type = p.location_type

    def csv_fields(self, location):
        details = [location.location_type, location.name]
        if location.parent:
            details.append(location.parent.location_type)
            details.append(location.parent.name)
        else:
            details.extend([None, None])

        if isinstance(location, Rack):
            details.append(location.rack_row)
            details.append(location.rack_column)
        else:
            details.extend([None, None])

        if hasattr(location, 'timezone'):
            details.append(location.timezone)
        else:
            details.extend([None])

        details.append(location.fullname)

        yield details

for location_type, mapper in Location.__mapper__.polymorphic_map.items():
    ObjectFormatter.handlers[mapper.class_] = LocationFormatter()
