# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013,2014,2015  Contributor
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

from datetime import datetime

from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        Sequence, UniqueConstraint)
from sqlalchemy.orm import relation, backref, validates, deferred

from aquilon.exceptions_ import InternalError
from aquilon.aqdb.column_types import AqStr
from aquilon.aqdb.model import Base, Cluster, Host

_TN = 'resource'
_RESHOLDER = 'resholder'


class ResourceHolder(Base):
    """
    Who owns this resource? This could be a variety of different
    owners (e.g. a host, a cluster) and so we have a polymorphic class
    to represent this ownership - that enforces that only a single class
    can ever have ownership. We enforce uniqueness of (resource name,
    resourceholder). As an example, you could have a filesystem resource
    called 'root' on many hosts.
    """
    __tablename__ = _RESHOLDER

    id = Column(Integer, Sequence('%s_id_seq' % _RESHOLDER), primary_key=True)

    # I don't like this as a string...
    holder_type = Column(AqStr(16), nullable=False)
    __mapper_args__ = {'polymorphic_on': holder_type,
                       'with_polymorphic': '*'}

    @property
    def holder_name(self):  # pragma: no cover
        raise InternalError("Abstract base method called")

    @property
    def holder_object(self):  # pragma: no cover
        raise InternalError("Abstract base method called")

    @property
    def toplevel_holder_object(self):
        return self.holder_object

    @validates('resources')
    def _validate_resources(self, key, value):
        return self.validate_resources(key, value)

    def validate_resources(self, key, value):  # pylint: disable=W0613
        return value

    def __format__(self, fmt):
        return format(self.holder_object, fmt)


class HostResource(ResourceHolder):
    host_id = Column(ForeignKey(Host.hardware_entity_id, ondelete='CASCADE'),
                     nullable=True, unique=True)

    # This is a one-to-one relation, so we need uselist=False on the backref
    host = relation(Host,
                    backref=backref('resholder', uselist=False,
                                    cascade='all, delete-orphan'))

    __mapper_args__ = {'polymorphic_identity': 'host'}

    @property
    def holder_name(self):
        return self.host.fqdn

    @property
    def holder_object(self):
        return self.host


class ClusterResource(ResourceHolder):
    cluster_id = Column(ForeignKey(Cluster.id, ondelete='CASCADE'),
                        nullable=True, unique=True)

    # This is a one-to-one relation, so we need uselist=False on the backref
    cluster = relation(Cluster,
                       backref=backref('resholder', uselist=False,
                                       cascade='all, delete-orphan'))

    __mapper_args__ = {'polymorphic_identity': 'cluster'}

    @property
    def holder_name(self):
        return self.cluster.name

    @property
    def holder_object(self):
        return self.cluster


class Resource(Base):
    """
        Abstraction of specific tables (e.g. VM or Filesystem) into a resource

        A resource is a generic bundle that can be attached to hosts or
        clusters. The resource can take on different shapes such as a VM
        or a filesystem, but there are many common operations we want
        to perform on them and therefore we map the specific types of
        bundles into this Resource class.
    """
    __tablename__ = _TN

    id = Column(Integer, Sequence('%s_id_seq' % _TN), primary_key=True)
    resource_type = Column(AqStr(16), nullable=False)
    name = Column(AqStr(64), nullable=False)
    creation_date = deferred(Column(DateTime, default=datetime.now,
                                    nullable=False))
    comments = Column(String(255), nullable=True)
    holder_id = Column(ForeignKey(ResourceHolder.id, ondelete='CASCADE'),
                       nullable=False, index=True)

    holder = relation(ResourceHolder, innerjoin=True,
                      backref=backref('resources',
                                      cascade='all, delete-orphan'))

    __table_args__ = (UniqueConstraint(holder_id, name, resource_type,
                                       name='%s_holder_name_type_uk' % _TN),
                      {'info': {'unique_fields': ['name', 'resource_type',
                                                  'holder']}})
    __mapper_args__ = {'polymorphic_on': resource_type}

    def __init__(self, name=None, **kwargs):
        name = AqStr.normalize(name)
        super(Resource, self).__init__(name=name, **kwargs)

    @validates('holder')
    def _validate_holder(self, key, value):
        return self.validate_holder(key, value)

    def validate_holder(self, key, value):  # pylint: disable=W0613
        return value

    def __repr__(self):
        return "<{0:c} Resource {0.name} of {1}>".format(self, self.holder.holder_object)
