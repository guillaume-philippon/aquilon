# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015  Contributor
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
"""Router address formatter."""


from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import RouterAddress


class RouterAddressFormatter(ObjectFormatter):

    def format_raw(self, router, indent="", embedded=True,
                   indirect_attrs=True):
        details = []
        if router.dns_records:
            names = ", ".join(sorted(str(dnsrec.fqdn) for dnsrec in
                                     router.dns_records))
        else:
            names = "unknown"

        details.append(indent + "Router: %s [%s]" % (names, router.ip))
        details.append(indent + "  {0:c}: {0!s}".format(router.network))
        details.append(indent + "  {0:c}: {0.name}".format(router.network.network_environment))
        if router.location:
            details.append(self.redirect_raw(router.location, indent + "  "))
        if router.comments:
            details.append(indent + "  Comments: %s" % router.comments)

        return "\n".join(details)


ObjectFormatter.handlers[RouterAddress] = RouterAddressFormatter()
