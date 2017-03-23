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
""" tables/classes applying to clusters """
import re
from datetime import datetime

from sqlalchemy import (Column, Integer, Boolean, String, DateTime, Sequence,
                        ForeignKey, UniqueConstraint, PrimaryKeyConstraint)
from sqlalchemy.orm import (object_session, relation, backref, deferred,
                            joinedload, validates)
from sqlalchemy.orm.attributes import set_committed_value
from sqlalchemy.ext.associationproxy import association_proxy

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.column_types import AqStr
from aquilon.aqdb.model import (Base, Host, Location, Personality,
                                ClusterLifecycle, NetworkDevice,
                                CompileableMixin)

# Cluster is a reserved word in Oracle
_TN = 'clstr'
_ETN = 'esx_cluster'
_HCM = 'host_cluster_member'
_CAP = 'clstr_allow_per'


def _hcm_host_creator(tuple):
    host = tuple[0]
    node_index = tuple[1]
    return HostClusterMember(host=host, node_index=node_index)


class Cluster(CompileableMixin, Base):
    """
        A group of two or more hosts for high availability or grid
        capabilities.  Location constraint is nullable as it may or
        may not be used.
    """
    __tablename__ = _TN

    id = Column(Integer, Sequence('%s_id_seq' % _TN), primary_key=True)
    cluster_type = Column(AqStr(16), nullable=False)
    name = Column(AqStr(64), nullable=False, unique=True)

    location_constraint_id = Column(ForeignKey(Location.id), nullable=False,
                                    index=True)

    preferred_location_id = Column(ForeignKey(Location.id,
                                              name="clstr_preferred_location_fk"),
                                   nullable=True, index=True)

    max_hosts = Column(Integer, nullable=True)
    # N+M clusters are defined by setting down_hosts_threshold to M
    # Simple 2-node clusters would have down_hosts_threshold of 0
    down_hosts_threshold = Column(Integer, nullable=True)
    # And that tolerance can be relaxed even further in maintenance windows
    down_maint_threshold = Column(Integer, nullable=True)
    # Some clusters (e.g. grid) don't want fixed N+M down_hosts_threshold, but
    # use percentage goals (i.e. don't alert until 5% of the population dies)
    down_hosts_percent = Column(Boolean, default=False, nullable=True)
    down_maint_percent = Column(Boolean, default=False, nullable=True)

    creation_date = deferred(Column(DateTime, default=datetime.now,
                                    nullable=False))
    status_id = Column(ForeignKey(ClusterLifecycle.id), nullable=False)
    comments = Column(String(255))

    status = relation(ClusterLifecycle, innerjoin=True)
    location_constraint = relation(Location, lazy=False, innerjoin=True,
                                   foreign_keys=location_constraint_id)
    preferred_location = relation(Location, foreign_keys=preferred_location_id)

    hosts = association_proxy('_hosts', 'host', creator=_hcm_host_creator)

    __table_args__ = ({'info': {'unique_fields': ['name']}},)
    __mapper_args__ = {'polymorphic_on': cluster_type}

    def __init__(self, name=None, **kwargs):
        name = AqStr.normalize(name)
        super(Cluster, self).__init__(name=name, **kwargs)

    @property
    def title(self):
        if self.archetype.outputdesc is not None:
            return self.archetype.outputdesc
        return self.archetype.name.capitalize() + " Cluster"

    @property
    def dht_value(self):
        if not self.down_hosts_percent:
            return self.down_hosts_threshold
        return self.down_hosts_threshold * len(self.hosts) // 100

    @property
    def dmt_value(self):
        if not self.down_maint_percent:
            return self.down_maint_threshold
        return self.down_maint_threshold * len(self.hosts) // 100

    @staticmethod
    def parse_threshold(threshold):
        is_percent = False
        percent = re.search(r'(\d+)(%)?', threshold)
        thresh_value = int(percent.group(1))
        if percent.group(2):
            is_percent = True
        return (is_percent, thresh_value)

    def member_locations(self, location_class=None):
        if location_class:
            attr = location_class.__mapper__.polymorphic_identity
        else:
            attr = None

        def filter(dblocation, attr):
            if attr is None:
                return dblocation
            # TODO: This may return None. Do we care?
            return getattr(dblocation, attr)

        return set(filter(host.hardware_entity.location, attr)
                   for host in self.hosts)

    @property
    def minimum_location(self):
        location = None
        for host in self.hosts:
            if location:
                location = location.merge(host.hardware_entity.location)
            else:
                location = host.hardware_entity.location
        return location

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
        for dbobj in self.hosts:
            yield dbobj

    @validates('_hosts')
    def validate_host_member(self, key, value):  # pylint: disable=W0613
        session = object_session(self)
        with session.no_autoflush:
            self.validate_membership(value.host)
        return value

    @validates('location_constraint')
    @validates('preferred_location')
    def validate_location_preference(self, key, value):
        if key == 'location_constraint':
            if (self.preferred_location and
                    value not in self.preferred_location.parents):
                raise ArgumentError("The new location constraint does not "
                                    "contain the preferred location.")
        elif key == 'preferred_location':
            if (value is not None and
                    self.location_constraint not in value.parents):
                raise ArgumentError("The new preferred location is not "
                                    "inside the location constraint.")
        return value

    def validate_membership(self, host):
        if self.allowed_personalities and \
                host.personality not in self.allowed_personalities:
            allowed = sorted(pers.qualified_name for pers in
                             self.allowed_personalities)
            raise ArgumentError("{0} is not allowed by the cluster.  Allowed "
                                "personalities are: {1!s}"
                                .format(host.personality, ", ".join(allowed)))

        if host.hardware_entity.location != self.location_constraint and \
                self.location_constraint not in \
                host.hardware_entity.location.parents:
            raise ArgumentError("Host location {0} is not within cluster "
                                "location {1}."
                                .format(host.hardware_entity.location,
                                        self.location_constraint))

        if host.branch != self.branch or \
                host.sandbox_author != self.sandbox_author:
            raise ArgumentError("{0} {1} {2} does not match {3:l} {4} {5}."
                                .format(host, host.branch.branch_type,
                                        host.authored_branch, self,
                                        self.branch.branch_type,
                                        self.authored_branch))

    def validate(self):
        session = object_session(self)
        q = session.query(HostClusterMember)
        q = q.filter_by(cluster=self)
        q = q.options(joinedload('host'),
                      joinedload('host.hardware_entity'))
        members = q.all()
        set_committed_value(self, '_hosts', members)

        if self.preferred_location:
            member_locs = self.member_locations(location_class=self.preferred_location.__class__)
            if self.preferred_location not in member_locs:
                raise ArgumentError("{0} has no members inside preferred {1:l}."
                                    .format(self, self.preferred_location))

        if self.max_hosts is not None and len(self.hosts) > self.max_hosts:
            raise ArgumentError("{0} has {1} hosts bound, which exceeds the "
                                "requested limit of {2}."
                                .format(self, len(self.hosts), self.max_hosts))
        if self.metacluster:
            self.metacluster.validate()

    def format_helper(self, format_spec, instance):
        # Based on format_helper() and _get_class_label() in Base
        lowercase = False
        class_only = False
        passthrough = ""
        for letter in format_spec:
            if letter == "l":
                lowercase = True
            elif letter == "c":
                class_only = True
            else:
                passthrough += letter

        if self.cluster_type == 'meta':
            clsname = self.title + " Metacluster"
        else:
            clsname = self.title + " Cluster"

        if lowercase:
            clsname = " ".join(x if x[:-1].isupper() else x.lower()
                               for x in clsname.split())
        if class_only:
            return clsname.__format__(passthrough)
        val = "%s %s" % (clsname, instance)
        return val.__format__(passthrough)


class ComputeCluster(Cluster):
    """
        A cluster containing computers - no special characteristics
    """
    __tablename__ = 'compute_cluster'
    _class_label = 'Compute Cluster'

    cluster_id = Column(ForeignKey(Cluster.id, ondelete='CASCADE'), primary_key=True)

    __table_args__ = ({'info': {'unique_fields': ['name']}},)
    __mapper_args__ = {'polymorphic_identity': 'compute'}


class StorageCluster(Cluster):
    """
        A cluster of storage devices
    """
    __tablename__ = 'storage_cluster'
    _class_label = 'Storage Cluster'

    cluster_id = Column(ForeignKey(Cluster.id, ondelete='CASCADE'), primary_key=True)

    __table_args__ = ({'info': {'unique_fields': ['name']}},)
    __mapper_args__ = {'polymorphic_identity': 'storage'}

    def validate_membership(self, host):
        super(StorageCluster, self).validate_membership(host)
        # FIXME: this should be in the configuration, not in the code
        if host.archetype.name != "filer":
            raise ArgumentError("Only hosts with archetype 'filer' can be "
                                "added to a storage cluster. {0} is "
                                "of {1:l}.".format(host, host.archetype))


# ESX Cluster is really a Grid Cluster, but we have
# specific broker-level behaviours we need to enforce

class EsxCluster(Cluster):
    """
        Specifically for our VMware esx based clusters.
    """
    __tablename__ = _ETN
    _class_label = 'ESX Cluster'

    esx_cluster_id = Column(ForeignKey(Cluster.id, ondelete='CASCADE'),
                            primary_key=True)

    network_device_id = Column(ForeignKey(NetworkDevice.hardware_entity_id),
                               nullable=True, index=True)

    network_device = relation(NetworkDevice, lazy=False,
                              backref=backref('esx_clusters'))

    __table_args__ = ({'info': {'unique_fields': ['name']}},)
    __mapper_args__ = {'polymorphic_identity': 'esx'}

    def validate(self):
        super(EsxCluster, self).validate()

        # It doesn't matter how many vmhosts we have if there are no
        # virtual machines.
        if len(self.virtual_machines) <= 0:
            return

        # For calculations, assume that down_hosts_threshold vmhosts
        # are not available from the number currently configured.
        if self.down_hosts_percent:
            adjusted_host_count = len(self.hosts) - \
                (self.down_hosts_threshold * len(self.hosts) // 100)
            dhtstr = "%d%%" % self.down_hosts_threshold
        else:
            adjusted_host_count = len(self.hosts) - self.down_hosts_threshold
            dhtstr = "%d" % self.down_hosts_threshold

        if adjusted_host_count <= 0:
            raise ArgumentError("%s cannot support VMs with %s "
                                "vmhosts and a down_hosts_threshold of %s" %
                                (format(self), len(self.hosts), dhtstr))

        return


class HostClusterMember(Base):
    """ Association table for clusters and their member hosts """
    __tablename__ = _HCM

    cluster_id = Column(ForeignKey(Cluster.id, ondelete='CASCADE'),
                        nullable=False)

    host_id = Column(ForeignKey(Host.hardware_entity_id, ondelete='CASCADE'),
                     nullable=False, unique=True)

    node_index = Column(Integer, nullable=False)

    # Association Proxy and relation cascading: We need cascade=all
    # on backrefs so that deletion propagates to avoid AssertionError:
    # Dependency rule tried to blank-out primary key column on deletion
    # of the Cluster and it's links. On the contrary do not have
    # cascade='all' on the forward mapper here, else deletion of
    # clusters and their links also causes deletion of hosts (BAD)
    cluster = relation(Cluster, innerjoin=True,
                       backref=backref('_hosts', cascade='all, delete-orphan',
                                       passive_deletes=True))

    # This is a one-to-one relation, so we need uselist=False on the backref
    host = relation(Host, innerjoin=True,
                    backref=backref('_cluster', uselist=False,
                                    cascade='all, delete-orphan',
                                    passive_deletes=True))

    __table_args__ = (PrimaryKeyConstraint(cluster_id, host_id),
                      UniqueConstraint(cluster_id, node_index,
                                       name='%s_node_uk' % _HCM),
                      {'info': {'unique_fields': ['cluster', 'host']}},)

Host.cluster = association_proxy('_cluster', 'cluster')


class __ClusterAllowedPersonality(Base):
    __tablename__ = _CAP

    cluster_id = Column(ForeignKey(Cluster.id, ondelete='CASCADE'),
                        nullable=False)

    personality_id = Column(ForeignKey(Personality.id, ondelete='CASCADE'),
                            nullable=False, index=True)

    __table_args__ = (PrimaryKeyConstraint(cluster_id, personality_id),)

Cluster.allowed_personalities = relation(Personality,
                                         secondary=__ClusterAllowedPersonality.__table__,
                                         passive_deletes=True)
