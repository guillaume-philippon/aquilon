# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014  Contributor
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

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Cluster, MetaCluster, Location
from aquilon.utils import validate_nlist_key
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.cluster import parse_cluster_arguments
from aquilon.worker.dbwrappers.location import get_location
from aquilon.worker.templates import Plenary


class CommandAddMetaCluster(BrokerCommand):

    required_parameters = ["metacluster"]

    def render(self, session, logger, metacluster, archetype, personality,
               domain, sandbox, max_members, buildstatus, comments,
               **arguments):
        validate_nlist_key("metacluster", metacluster)
        if metacluster.strip().lower() == 'global':
            raise ArgumentError("Metacluster name global is reserved.")

        MetaCluster.get_unique(session, metacluster, preclude=True)
        # Clusters and metaclusters share the same namespace, so provide a nice
        # error message if a cluster with the same name exists
        Cluster.get_unique(session, metacluster, preclude=True)

        # This should be reverted when virtbuild supports these options
        if not archetype:
            archetype = "metacluster"

        kw = parse_cluster_arguments(session, self.config, archetype,
                                     personality, domain, sandbox, buildstatus,
                                     max_members)
        max_clusters = kw.pop('max_members')

        dbloc = get_location(session, **arguments)

        # This should be reverted when virtbuild supports this option
        if not dbloc:
            section = "archetype_" + kw['personality'].archetype.name
            dbloc = Location.get_unique(session,
                                        name=self.config.get(section,
                                                             "location_name"),
                                        location_type=self.config.get(section,
                                                                      "location_type"))
        elif not dbloc.campus:
            raise ArgumentError("{0} is not within a campus.".format(dbloc))

        dbcluster = MetaCluster(name=metacluster, location_constraint=dbloc,
                                max_clusters=max_clusters, comments=comments,
                                **kw)

        session.add(dbcluster)
        session.flush()

        plenary = Plenary.get_plenary(dbcluster, logger=logger)
        plenary.write()

        return
