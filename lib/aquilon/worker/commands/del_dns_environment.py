# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2015,2016  Contributor
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
"""Contains the logic for `aq del dns environment`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand
from aquilon.aqdb.model import DnsEnvironment, Fqdn


class CommandDelDnsEnvironment(BrokerCommand):

    required_parameters = ["dns_environment"]

    def render(self, session, dns_environment, **_):
        db_dnsenv = DnsEnvironment.get_unique(session, dns_environment,
                                              compel=True)

        if db_dnsenv.is_default:
            raise ArgumentError("{0} is the default DNS environment, "
                                "therefore it cannot be deleted."
                                .format(db_dnsenv))
        q = session.query(Fqdn.id)
        q = q.filter_by(dns_environment=db_dnsenv)
        if q.count():
            raise ArgumentError("{0} is still in use by DNS records, and "
                                "cannot be deleted.".format(db_dnsenv))

        session.delete(db_dnsenv)
        session.flush()

        return
