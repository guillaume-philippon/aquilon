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
"""RebootIntervention Resource formatter."""

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.resource import ResourceFormatter
from aquilon.aqdb.model import RebootIntervention


class RebootInterventionFormatter(ResourceFormatter):

    suppress_name = True

    def extra_details(self, rs, indent=""):
        details = []
        details.append(indent + "  Start: {0.start_date}".format(rs))
        details.append(indent + "  Expiry: {0.expiry_date}".format(rs))
        details.append(indent + "  Reason: {0.reason}".format(rs))
        return details

    def fill_proto(self, rs, skeleton, embedded=True, indirect_attrs=True):
        super(RebootInterventionFormatter, self).fill_proto(rs, skeleton)
        # XXX: The protocol does not have an rsdata field, and even if it
        # did, why would reboot intervention fill it in?  Could use ivdata,
        # not sure if we want a separate rivdata.
        # skeleton.rsdata.start_date = rs.start_date
        # skeleton.rsdata.expiry_date = rs.expiry_date
        # skeleton.rsdata.justification = rs.justification

ObjectFormatter.handlers[RebootIntervention] = RebootInterventionFormatter()
