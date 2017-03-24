# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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

from operator import attrgetter

from sqlalchemy.orm.session import object_session

from aquilon.aqdb.model import Cluster, ClusterResource, MetaCluster, Share
from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.compileable import CompileableFormatter


class MetaClusterFormatter(CompileableFormatter):
    def format_raw(self, metacluster, indent="", embedded=True,
                   indirect_attrs=True):
        details = [indent + "MetaCluster: %s" % metacluster.name]
        details.append(indent + "  Member Location Constraint:")
        details.append(self.redirect_raw(metacluster.location_constraint,
                                         indent + "    "))
        details.append(indent + "  Max members: %s" % metacluster.max_clusters)
        details.append(self.redirect_raw(metacluster.status, indent + "  "))
        details.append(self.redirect_raw(metacluster.personality_stage,
                                         indent + "  "))
        details.append(indent + "  {0:c}: {1}"
                       .format(metacluster.branch, metacluster.authored_branch))

        if metacluster.virtual_switch:
            details.append(self.redirect_raw(metacluster.virtual_switch,
                                             indent + "  "))

        for dbsi in metacluster.services_used:
            details.append(indent +
                           "  Member Alignment: Service %s Instance %s" %
                           (dbsi.service.name, dbsi.name))
        for personality in metacluster.allowed_personalities:
            details.append(indent + "  Allowed {0:c}: {0.name} {1:c}: {1.name}"
                           .format(personality, personality.archetype))
        for cluster in metacluster.members:
            details.append(indent + "  Member: {0}".format(cluster))

        if metacluster.resholder and metacluster.resholder.resources:
            details.append(indent + "  Resources:")
            for resource in sorted(metacluster.resholder.resources,
                                   key=attrgetter('resource_type', 'name')):
                details.append(self.redirect_raw(resource, indent + "    "))

        # for v1 shares
        q = object_session(metacluster).query(Share.name).distinct()
        q = q.join(ClusterResource, Cluster)
        q = q.filter_by(metacluster=metacluster)
        q = q.order_by(Share.name)
        shares = q.all()

        for share_name in shares:
            details.append(indent + "  Share: %s" % share_name)

        if metacluster.comments:
            details.append(indent + "  Comments: %s" % metacluster.comments)
        return "\n".join(details)

    def fill_proto(self, metacluster, skeleton, embedded=True,
                   indirect_attrs=True):
        super(MetaClusterFormatter, self).fill_proto(metacluster, skeleton)

        skeleton.name = metacluster.name
        self.redirect_proto(metacluster.members, skeleton.clusters)
        self.redirect_proto(metacluster.location_constraint,
                            skeleton.location_constraint)

        if metacluster.max_clusters is not None:
            skeleton.max_members = metacluster.max_clusters

        if metacluster.resholder and metacluster.resholder.resources:
            self.redirect_proto(metacluster.resholder.resources,
                                skeleton.resources)

        self.redirect_proto(metacluster.services_used, skeleton.services_used,
                            indirect_attrs=False)
        self.redirect_proto(metacluster.allowed_personalities,
                            skeleton.allowed_personalities,
                            indirect_attrs=False)

        if metacluster.virtual_switch:
            self.redirect_proto(metacluster.virtual_switch,
                                skeleton.virtual_switch)

ObjectFormatter.handlers[MetaCluster] = MetaClusterFormatter()
