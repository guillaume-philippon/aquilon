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
"""Contains the logic for `aq update alias`."""

from aquilon.aqdb.model import Alias, DnsEnvironment
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.dns import (create_target_if_needed,
                                           delete_target_if_needed)
from aquilon.worker.dbwrappers.grn import lookup_grn
from aquilon.worker.processes import DSDBRunner


class CommandUpdateAlias(BrokerCommand):

    required_parameters = ["fqdn"]

    def render(self, session, logger, fqdn, dns_environment, target,
               target_environment, ttl, clear_ttl, grn, eon_id, clear_grn,
               comments, **_):
        dbdns_env = DnsEnvironment.get_unique_or_default(session,
                                                         dns_environment)

        if target_environment:
            dbtgt_env = DnsEnvironment.get_unique_or_default(session,
                                                             target_environment)
        else:
            dbtgt_env = dbdns_env

        dbalias = Alias.get_unique(session, fqdn=fqdn,
                                   dns_environment=dbdns_env, compel=True)

        old_target_fqdn = str(dbalias.target.fqdn)
        old_comments = dbalias.comments

        if grn or eon_id:
            dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                               config=self.config)
            dbalias.owner_grn = dbgrn
        elif clear_grn:
            dbalias.owner_grn = None

        if target or target_environment:
            old_target = dbalias.target
            dbalias.target = create_target_if_needed(session, logger,
                                                     target, dbtgt_env)

            # TODO: at some day we should verify that the new target is also
            # bound as a server, and modify the ServiceInstanceServer bindings
            # accordingly
            for srv in dbalias.services_provided:
                if srv.host or srv.cluster:
                    provider = srv.host or srv.cluster
                    logger.client_info("Warning: {0} provides {1:l}, and is "
                                       "bound to {2:l}. Updating the target of "
                                       "the alias may leave that server "
                                       "binding in an inconsistent state."
                                       .format(dbalias, srv.service_instance,
                                               provider))

            if dbalias.target != old_target:
                delete_target_if_needed(session, old_target)

        if ttl is not None:
            dbalias.ttl = ttl
        elif clear_ttl:
            dbalias.ttl = None

        if comments is not None:
            dbalias.comments = comments

        session.flush()

        if dbdns_env.is_default and dbalias.fqdn.dns_domain.name == "ms.com":
            dsdb_runner = DSDBRunner(logger=logger)
            dsdb_runner.update_alias(fqdn, dbalias.target.fqdn,
                                     dbalias.comments, old_target_fqdn,
                                     old_comments)
            dsdb_runner.commit_or_rollback("Could not update alias in DSDB")

        return
