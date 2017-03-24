# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2013,2014,2016  Contributor
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

from aquilon.aqdb.model import Vendor
from aquilon.worker.broker import BrokerCommand
from aquilon.utils import validate_template_name


class CommandAddVendor(BrokerCommand):

    required_parameters = ["vendor"]

    def render(self, session, vendor, comments, **_):
        validate_template_name("--vendor", vendor)
        Vendor.get_unique(session, vendor, preclude=True)

        dbv = Vendor(name=vendor, comments=comments)
        session.add(dbv)
        return
