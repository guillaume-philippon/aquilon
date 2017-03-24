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

from aquilon.aqdb.model import NsRecord, DnsDomain, ARecord
from aquilon.worker.broker import BrokerCommand
from aquilon.exceptions_ import NotFoundException


class CommandShowNsRecord(BrokerCommand):

    required_parameters = ["dns_domain", "fqdn"]

    def render(self, session, dns_domain, **kw):
        dbdns = DnsDomain.get_unique(session, dns_domain, compel=True)
        q = session.query(NsRecord).filter_by(dns_domain=dbdns)

        dba_record = ARecord.get_unique(session, fqdn=kw['fqdn'], compel=True)
        q = q.filter_by(a_record=dba_record)
        ns_rec = q.all()

        if not ns_rec:
            raise NotFoundException(
                "Could not find a dns_record for domain '%s'." % dns_domain)

        return ns_rec
