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

from aquilon.aqdb.model import (Cluster, EsxCluster, ComputeCluster,
                                StorageCluster)
from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.compileable import CompileableFormatter


class ClusterFormatter(CompileableFormatter):
    def fill_proto(self, cluster, skeleton, embedded=True,
                   indirect_attrs=True):
        super(ClusterFormatter, self).fill_proto(cluster, skeleton)

        skeleton.name = cluster.name
        skeleton.threshold = cluster.down_hosts_threshold
        skeleton.threshold_is_percent = cluster.down_hosts_percent
        if cluster.down_maint_threshold is not None:
            skeleton.maint_threshold = cluster.down_maint_threshold
            skeleton.maint_threshold_is_percent = \
                cluster.down_maint_percent

        self.redirect_proto(cluster.hosts, skeleton.hosts)
        self.redirect_proto(cluster.location_constraint,
                            skeleton.location_constraint)

        if cluster.max_hosts is not None:
            skeleton.max_members = cluster.max_hosts

        if cluster.metacluster:
            skeleton.metacluster = cluster.metacluster.name

        if cluster.resholder and cluster.resholder.resources:
            self.redirect_proto(cluster.resholder.resources, skeleton.resources)

        self.redirect_proto(cluster.services_used, skeleton.aligned_services,
                            indirect_attrs=False)
        self.redirect_proto(cluster.allowed_personalities,
                            skeleton.allowed_personalities,
                            indirect_attrs=False)

        if cluster.virtual_switch:
            self.redirect_proto(cluster.virtual_switch,
                                skeleton.virtual_switch)

        if cluster.cluster_group:
            for member in cluster.cluster_group.members:
                if member == cluster:
                    continue
                gskel = skeleton.grouped_cluster.add()
                gskel.name = member.name

    def format_raw(self, cluster, indent="", embedded=True,
                   indirect_attrs=True):
        details = [indent + "{0:c}: {0.name}".format(cluster)]
        if cluster.metacluster:
            details.append(indent +
                           "  {0:c}: {0.name}".format(cluster.metacluster))
        details.append(indent + "  Member Location Constraint:")
        details.append(self.redirect_raw(cluster.location_constraint,
                                         indent + "    "))
        if cluster.preferred_location:
            details.append(indent + "  Preferred {0:c}: {0.name}"
                           .format(cluster.preferred_location))
        if cluster.max_hosts is None:
            details.append(indent + "  Max members: unlimited")
        else:
            details.append(indent + "  Max members: %s" % cluster.max_hosts)

        if cluster.down_hosts_percent:
            dht = cluster.down_hosts_threshold * len(cluster.hosts) // 100
            details.append(indent + "  Down Hosts Threshold: %s (%s%%)" %
                           (dht, cluster.down_hosts_threshold))
        else:
            details.append(indent + "  Down Hosts Threshold: %s" %
                           cluster.down_hosts_threshold)

        if cluster.down_maint_threshold is not None:
            if cluster.down_maint_percent:
                dht = cluster.down_maint_threshold * len(cluster.hosts) // 100
                details.append(indent + "  Maintenance Threshold: %s (%s%%)" %
                               (dht, cluster.down_maint_threshold))
            else:
                details.append(indent + "  Maintenance Threshold: %s" %
                               cluster.down_maint_threshold)

        if cluster.cluster_group:
            for member in cluster.cluster_group.members:
                if member == cluster:
                    continue
                details.append("  Grouped with {0:c}: {0.name}".format(member))

        if cluster.resholder and cluster.resholder.resources:
            details.append(indent + "  Resources:")
            for resource in sorted(cluster.resholder.resources,
                                   key=attrgetter('resource_type', 'name')):
                details.append(self.redirect_raw(resource, indent + "    "))

        if cluster.virtual_switch:
            details.append(self.redirect_raw(cluster.virtual_switch,
                                             indent + "  "))

        if isinstance(cluster, EsxCluster):
            details.append(indent + "  Virtual Machine count: %s" %
                           len(cluster.virtual_machines))
            details.append(indent + "  ESX VMHost count: %s" %
                           len(cluster.hosts))
            if cluster.network_device:
                details.append(indent + "  {0:c}: {0!s}".format(cluster.network_device))
        details.append(self.redirect_raw(cluster.status, indent + "  "))
        details.append(self.redirect_raw(cluster.personality_stage,
                                         indent + "  "))
        details.append(indent + "  {0:c}: {1}"
                       .format(cluster.branch, cluster.authored_branch))
        for dbsi in cluster.services_used:
            details.append(indent +
                           "  Member Alignment: Service %s Instance %s" %
                           (dbsi.service.name, dbsi.name))
        for srv in sorted(cluster.services_provided,
                          key=attrgetter("service_instance.service.name",
                                         "service_instance.name")):
            details.append(indent + "  Provides Service: %s Instance: %s"
                           % (srv.service_instance.service.name,
                              srv.service_instance.name))
            details.append(self.redirect_raw(srv, indent + "    "))
        for personality in cluster.allowed_personalities:
            details.append(indent + "  Allowed {0:c}: {0.name} {1:c}: {1.name}"
                           .format(personality, personality.archetype))
        for member in sorted(cluster._hosts, key=attrgetter("host.fqdn")):
            details.append(indent + "  Member: %s [node_index: %d]" %
                           (member.host.fqdn, member.node_index))
        if cluster.comments:
            details.append(indent + "  Comments: %s" % cluster.comments)
        return "\n".join(details)

ObjectFormatter.handlers[Cluster] = ClusterFormatter()
ObjectFormatter.handlers[EsxCluster] = ClusterFormatter()
ObjectFormatter.handlers[ComputeCluster] = ClusterFormatter()
ObjectFormatter.handlers[StorageCluster] = ClusterFormatter()
