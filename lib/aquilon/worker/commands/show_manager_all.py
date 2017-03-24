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
"""Contains the logic for `aq show manager --all`."""

from sqlalchemy.orm import contains_eager
from sqlalchemy.sql import and_

from aquilon.aqdb.model import (AddressAssignment, ManagementInterface, ARecord,
                                DnsDomain, Fqdn)
from aquilon.worker.broker import BrokerCommand


class CommandShowManagerAll(BrokerCommand):

    def render(self, session, **_):
        q = session.query(ARecord)
        q = q.join((AddressAssignment,
                    and_(ARecord.network_id == AddressAssignment.network_id,
                         ARecord.ip == AddressAssignment.ip)))
        q = q.join(AddressAssignment.interface.of_type(ManagementInterface))
        q = q.reset_joinpoint()
        q = q.join(ARecord.fqdn, DnsDomain)
        q = q.options(contains_eager('fqdn'),
                      contains_eager('fqdn.dns_domain'))
        q = q.order_by(Fqdn.name, DnsDomain.name)
        return [rec.fqdn for rec in q]
