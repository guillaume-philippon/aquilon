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

from sqlalchemy.orm import joinedload, subqueryload

from aquilon.exceptions_ import NotFoundException
from aquilon.aqdb.model import Cluster, VirtualMachine, ClusterResource
from aquilon.worker.broker import BrokerCommand


class CommandShowClusterCluster(BrokerCommand):

    required_parameters = ['cluster']
    query_class = Cluster

    def render(self, session, cluster, **_):
        q = session.query(self.query_class)
        if self.query_class == Cluster:
            q = q.filter(Cluster.cluster_type != 'meta')
        vm_q = session.query(VirtualMachine)
        vm_q = vm_q.join(ClusterResource, Cluster)

        q = q.filter_by(name=cluster)
        vm_q = vm_q.filter_by(name=cluster)

        vm_q = vm_q.options(joinedload('machine'),
                            joinedload('machine.primary_name'),
                            joinedload('machine.primary_name.fqdn'))

        q = q.options(subqueryload('_hosts'),
                      joinedload('_hosts.host'),
                      joinedload('_hosts.host.hardware_entity'),
                      subqueryload('metacluster'),
                      joinedload('resholder'),
                      subqueryload('resholder.resources'),
                      subqueryload('services_used'),
                      subqueryload('allowed_personalities'))
        q = q.order_by(self.query_class.name)
        dbclusters = q.all()
        if cluster and not dbclusters:
            raise NotFoundException("Cluster %s not found." % cluster)

        # Manual eager-loading of VM resources. All the code does is making sure
        # the data is pinned in the session's cache
        machines = {vm.machine.hardware_entity_id: vm for vm in vm_q}  # pylint: disable=W0612

        return dbclusters
