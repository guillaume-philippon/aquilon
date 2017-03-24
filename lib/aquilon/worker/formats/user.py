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
"""UserPrincipal formatter."""


from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import User


class UserFormatter(ObjectFormatter):
    def format_raw(self, user, indent="", embedded=True, indirect_attrs=True):
        details = [indent + "User: %s" % user.name]
        details.append(indent + "  UID: %s" % user.uid)
        details.append(indent + "  GID: %s" % user.gid)
        details.append(indent + "  Full Name: %s" % user.full_name)
        details.append(indent + "  Home Directory: %s" % user.home_dir)
        return "\n".join(details)

    def csv_fields(self, user):
        yield (user.name, user.uid, user.gid, user.name, user.home_dir)

ObjectFormatter.handlers[User] = UserFormatter()
