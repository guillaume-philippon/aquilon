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
"""Contains the logic for `aq add alias`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import DnsRecord, Alias, Fqdn, DnsEnvironment
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.dns import create_target_if_needed
from aquilon.worker.dbwrappers.grn import lookup_grn
from aquilon.worker.processes import DSDBRunner


class CommandAddAlias(BrokerCommand):

    required_parameters = ["fqdn", "target"]

    def render(self, session, logger, fqdn, dns_environment, target,
               target_environment, ttl, grn, eon_id, comments, **_):
        dbdns_env = DnsEnvironment.get_unique_or_default(session,
                                                         dns_environment)
        if target_environment:
            dbtgt_env = DnsEnvironment.get_unique_or_default(session,
                                                             target_environment)
        else:
            dbtgt_env = dbdns_env

        dbfqdn = Fqdn.get_or_create(session, dns_environment=dbdns_env,
                                    fqdn=fqdn)

        if dbfqdn.dns_domain.restricted:
            raise ArgumentError("{0} is restricted, aliases are not allowed."
                                .format(dbfqdn.dns_domain))

        DnsRecord.get_unique(session, fqdn=dbfqdn, preclude=True)

        dbtarget = create_target_if_needed(session, logger, target, dbtgt_env)

        dbgrn = None
        if grn or eon_id:
            dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                               config=self.config)
        try:
            db_record = Alias(fqdn=dbfqdn, target=dbtarget, ttl=ttl,
                              owner_grn=dbgrn, comments=comments)
            session.add(db_record)
        except ValueError as err:
            raise ArgumentError(err)

        session.flush()

        if dbdns_env.is_default and dbfqdn.dns_domain.name == "ms.com" and \
           not dbtarget.dns_domain.restricted:
            dsdb_runner = DSDBRunner(logger=logger)
            dsdb_runner.add_alias(fqdn, target, comments)
            dsdb_runner.commit_or_rollback("Could not add alias to DSDB")

        return
