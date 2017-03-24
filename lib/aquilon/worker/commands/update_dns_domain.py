# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2016  Contributor
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
"""Contains the logic for `aq update dns domain`."""

from aquilon.aqdb.model import DnsDomain
from aquilon.worker.broker import BrokerCommand


class CommandUpdateDnsDomain(BrokerCommand):

    required_parameters = ["dns_domain"]

    def render(self, session, dns_domain, restricted, comments, **_):
        dbdns_domain = DnsDomain.get_unique(session, dns_domain, compel=True)
        if restricted is not None:
            dbdns_domain.restricted = restricted
        if comments is not None:
            dbdns_domain.comments = comments
        session.flush()
