# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017  Contributor
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
"""Contains the logic for `aq map grn`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import (Personality, PersonalityGrnMap, HostGrnMap,
                                Cluster)
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.change_management import validate_prod_personality
from aquilon.worker.dbwrappers.grn import lookup_grn
from aquilon.worker.dbwrappers.host import (hostname_to_host, hostlist_to_hosts,
                                            check_hostlist_size)


class CommandMapGrn(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["target"]
    require_usable_grn = True

    def _update_dbobj(self, obj, target, grn, mapcls):
        # Don't add twice the same tuple
        for grn_rec in obj.grns:
            if grn == grn_rec.grn and target == grn_rec.target:
                return

        obj.grns.append(mapcls(grn=grn, target=target))

    def render(self, session, logger, plenaries, target, grn, eon_id, hostname, list,
               membersof, personality, personality_stage, archetype,
               justification, reason, user, **_):
        dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                           config=self.config,
                           usable_only=self.require_usable_grn)


        if hostname:
            objs = [hostname_to_host(session, hostname)]
            mapcls = HostGrnMap
            config_key = "host_grn_targets"
        elif list:
            check_hostlist_size(self.command, self.config, list)
            objs = hostlist_to_hosts(session, list)
            mapcls = HostGrnMap
            config_key = "host_grn_targets"
        elif membersof:
            dbcluster = Cluster.get_unique(session, membersof, compel=True)
            objs = dbcluster.hosts
            mapcls = HostGrnMap
            config_key = "host_grn_targets"
        elif personality:
            dbpersonality = Personality.get_unique(session, name=personality,
                                                   archetype=archetype,
                                                   compel=True)
            objs = [dbpersonality.active_stage(personality_stage)]
            mapcls = PersonalityGrnMap
            config_key = "personality_grn_targets"
            validate_prod_personality(objs[0], user, justification, reason, logger)
        for obj in objs:
            section = "archetype_" + obj.archetype.name

            if self.config.has_option(section, config_key):
                valid_targets = [s.strip() for s in
                                 self.config.get(section, config_key).split(",")]
            else:
                raise ArgumentError("{0} has no valid GRN targets configured."
                                    .format(obj.archetype))

            if target not in valid_targets:
                raise ArgumentError("Invalid target %s for archetype %s, please "
                                    "choose from: %s." %
                                    (target, obj.archetype.name,
                                     ", ".join(valid_targets)))

            plenaries.add(obj)
            self._update_dbobj(obj, target, dbgrn, mapcls)

        session.flush()

        plenaries.write()

        return
