# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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
"""Contains the logic for `aq show host --all`."""

from sqlalchemy.orm import contains_eager, lazyload

from aquilon.aqdb.model import Host, HardwareEntity, DnsRecord, DnsDomain, Fqdn
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.formats.list import StringAttributeList


class CommandShowHostAll(BrokerCommand):

    def render(self, session, **_):
        q = session.query(Host)
        q = q.join(HardwareEntity, DnsRecord, (Fqdn, DnsRecord.fqdn_id == Fqdn.id),
                   DnsDomain)
        q = q.options(lazyload('branch'),
                      lazyload('personality_stage'),
                      contains_eager('hardware_entity'),
                      contains_eager('hardware_entity.primary_name'),
                      contains_eager('hardware_entity.primary_name.fqdn'),
                      contains_eager('hardware_entity.primary_name.fqdn.dns_domain'))
        q = q.order_by(Fqdn.name, DnsDomain.name)
        return StringAttributeList(q.all(), "fqdn")
