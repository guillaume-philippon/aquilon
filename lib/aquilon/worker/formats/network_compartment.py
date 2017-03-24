# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2013,2014,2015,2017  Contributor
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
"""Network environment formatter."""

from aquilon.aqdb.model import NetworkCompartment
from aquilon.worker.formats.formatters import ObjectFormatter


class NetworkCompartmentFormatter(ObjectFormatter):
    def format_raw(self, netcomp, indent="", embedded=True,
                   indirect_attrs=True):
        details = [indent + "{0:c}: {0.name}".format(netcomp)]
        if netcomp.comments:
            details.append(indent + "  Comments: %s" % netcomp.comments)
        return "\n".join(details)

    def csv_fields(self, network_compartment):
        yield(network_compartment.name, network_compartment.comments)

    def fill_proto(self, network_compartment, skeleton, embedded = True,
                    indirect_attrs=True):
        skeleton.name = network_compartment.name

ObjectFormatter.handlers[NetworkCompartment] = NetworkCompartmentFormatter()
