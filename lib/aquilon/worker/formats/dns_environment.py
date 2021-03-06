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
"""DNS Domain formatter."""

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import DnsEnvironment


class DnsEnvironmentFormatter(ObjectFormatter):
    def format_raw(self, dns_environment, indent="", embedded=True,
                   indirect_attrs=True):
        details = [indent + "{0:c}: {0!s}".format(dns_environment)]
        if dns_environment.comments:
            details.append(indent + "  Comments: %s" % dns_environment.comments)
        return "\n".join(details)

ObjectFormatter.handlers[DnsEnvironment] = DnsEnvironmentFormatter()
