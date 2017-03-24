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
"""Service Address Resource formatter."""

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.resource import ResourceFormatter
from aquilon.aqdb.model import ServiceAddress


class ServiceAddressFormatter(ResourceFormatter):
    def extra_details(self, srv, indent=""):
        details = []
        details.append(indent + "  Address: {0:a}".format(srv.dns_record))
        if srv.interfaces:
            details.append(indent + "  Interfaces: %s" %
                           ", ".join(sorted(iface.name for iface in
                                            srv.interfaces)))
        return details

    def fill_proto(self, srv, skeleton, embedded=True, indirect_attrs=True):
        super(ServiceAddressFormatter, self).fill_proto(srv, skeleton)
        skeleton.service_address.ip = str(srv.ip)
        skeleton.service_address.fqdn = str(srv.dns_record)
        skeleton.service_address.interfaces.extend(iface.name for iface in
                                                   srv.interfaces)

ObjectFormatter.handlers[ServiceAddress] = ServiceAddressFormatter()
