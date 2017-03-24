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
"""Contains the logic for `aq make`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import (Archetype, HostLifecycle,
                                OperatingSystem, Personality)
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.grn import lookup_grn
from aquilon.worker.dbwrappers.host import hostname_to_host
from aquilon.worker.templates import TemplateDomain
from aquilon.worker.services import Chooser


class CommandMake(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["hostname"]

    def render(self, session, logger, plenaries, hostname, osname, osversion, archetype,
               personality, personality_stage, buildstatus, keepbindings, grn,
               eon_id, cleargrn, comments, **_):
        dbhost = hostname_to_host(session, hostname)
        old_archetype = dbhost.archetype

        if archetype:
            dbarchetype = Archetype.get_unique(session, archetype, compel=True)
            if dbarchetype.cluster_type is not None:
                raise ArgumentError("{0} is a cluster archetype, it cannot be "
                                    "used for hosts.".format(dbarchetype))
        else:
            dbarchetype = dbhost.archetype

        if personality or personality_stage or old_archetype != dbarchetype:
            if not personality:
                personality = dbhost.personality.name

            dbpersonality = Personality.get_unique(session, name=personality,
                                                   archetype=dbarchetype,
                                                   compel=True)

            if dbhost.cluster and dbhost.cluster.allowed_personalities and \
               dbpersonality not in dbhost.cluster.allowed_personalities:
                allowed = sorted(pers.qualified_name for pers in
                                 dbhost.cluster.allowed_personalities)
                raise ArgumentError("{0} is not allowed by {1}.  "
                                    "Specify one of: {2}."
                                    .format(dbpersonality, dbhost.cluster,
                                            ", ".join(allowed)))

            dbhost.personality_stage = dbpersonality.default_stage(personality_stage)

        if osname or osversion or old_archetype != dbarchetype:
            if not osname:
                osname = dbhost.operating_system.name
            if not osversion:
                osversion = dbhost.operating_system.version

            dbos = OperatingSystem.get_unique(session, name=osname,
                                              version=osversion,
                                              archetype=dbarchetype,
                                              compel=True)
            # Hmm... no cluster constraint here...
            dbhost.operating_system = dbos

        if buildstatus:
            dbstatus = HostLifecycle.get_instance(session, buildstatus)
            dbhost.status.transition(dbhost, dbstatus)

        if grn or eon_id:
            dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                               config=self.config)
            dbhost.owner_grn = dbgrn

        if cleargrn:
            dbhost.owner_grn = None

        if comments is not None:
            dbhost.comments = comments

        session.flush()

        chooser = Chooser(dbhost, plenaries, logger=logger, required_only=not
                          keepbindings)
        chooser.set_required()

        session.flush()

        td = TemplateDomain(dbhost.branch, dbhost.sandbox_author, logger=logger)

        with plenaries.transaction():
            td.compile(session, only=plenaries.object_templates)

        return
