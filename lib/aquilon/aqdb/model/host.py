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
""" The majority of the things we're interested in for now are hosts. """

from datetime import datetime

from sqlalchemy import (Boolean, DateTime, String, Column, ForeignKey,
                        PrimaryKeyConstraint)
from sqlalchemy.orm import relation, backref, deferred

from aquilon.aqdb.model import (Base, HardwareEntity, HostLifecycle, Grn,
                                OperatingSystem, CompileableMixin)

from aquilon.aqdb.column_types import AqStr

_TN = 'host'
_HOSTGRN = 'host_grn_map'


class Host(CompileableMixin, Base):
    """ The Host class captures the configuration profile of a machine.

        Putting a physical machine into a chassis and powering it up leaves it
        in a state with a few more attributes not filled in: what Branch
        configures this host? If Ownership is captured, this is the place for
        it.

        Post DNS changes the class name "Host", and it's current existence may
        not make much sense. In the interest of keeping the scope of changes
        somewhat limited (compared to how much else is changing), the class is
        being left in this intermediate state, for the time being. The full
        expression of the changes would be to call the class "MachineProfile",
        and remove any machine specific information. This would provide a more
        normalized schema, rather than individual machines having all of the
        rows below, which potentially would need to be nullable.
    """

    __tablename__ = _TN
    _instance_label = 'fqdn'

    hardware_entity_id = Column(ForeignKey(HardwareEntity.id), primary_key=True)

    lifecycle_id = Column(ForeignKey(HostLifecycle.id), nullable=False)

    operating_system_id = Column(ForeignKey(OperatingSystem.id), nullable=False)

    owner_eon_id = Column(ForeignKey(Grn.eon_id, name='%s_owner_grn_fk' % _TN),
                          nullable=True)

    # something to retain the advertised status of the host
    advertise_status = Column(Boolean, nullable=False, default=False)

    creation_date = deferred(Column(DateTime, default=datetime.now,
                                    nullable=False))

    comments = deferred(Column(String(255), nullable=True))

    # This is a one-to-one relation, so we need uselist=False on the backref
    hardware_entity = relation(HardwareEntity, innerjoin=True,
                               backref=backref('host', uselist=False,
                                               cascade='all, delete-orphan'))

    status = relation(HostLifecycle, innerjoin=True)
    operating_system = relation(OperatingSystem, innerjoin=True)
    owner_grn = relation(Grn)

    @property
    def fqdn(self):
        return self.hardware_entity.fqdn

    # see cluster.py
    @property
    def virtual_machines(self):
        mach = []
        if self.resholder:
            for res in self.resholder.resources:
                # TODO: support virtual machines inside resource groups?
                if res.resource_type == "virtual_machine":
                    mach.append(res.machine)
        return mach

    def all_objects(self):
        yield self

    @property
    def effective_owner_grn(self):
        if self.owner_grn:
            return self.owner_grn
        else:
            return self.personality_stage.owner_grn

    @property
    def required_services(self):
        # Order matters in case the same key is present in both
        rqs = {dbsrv: None for dbsrv in self.operating_system.required_services}
        rqs.update(super(Host, self).required_services)
        return rqs


class HostGrnMap(Base):
    __tablename__ = _HOSTGRN

    host_id = Column(ForeignKey(Host.hardware_entity_id, ondelete="CASCADE"),
                     nullable=False)

    eon_id = Column(ForeignKey(Grn.eon_id), nullable=False)

    target = Column(AqStr(32), nullable=False)

    grn = relation(Grn, lazy=False, innerjoin=True)

    __table_args__ = (PrimaryKeyConstraint(host_id, eon_id, target),)

Host.grns = relation(HostGrnMap, cascade='all, delete-orphan',
                     passive_deletes=True)
