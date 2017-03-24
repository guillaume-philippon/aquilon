# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014  Contributor
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
""" GRN formatter """

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import Grn


class GrnFormatter(ObjectFormatter):

    def format_raw(self, grn, indent="", embedded=True, indirect_attrs=True):
        details = [indent + "{0:c}: {0.grn}".format(grn),
                   indent + "  EON ID: %d" % grn.eon_id,
                   indent + "  Disabled: %s" % grn.disabled]
        return "\n".join(details)

ObjectFormatter.handlers[Grn] = GrnFormatter()
