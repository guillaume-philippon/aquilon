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
""" The module governing tables and objects that represent what are known as
    Services (defined below) in Aquilon.

    Many important tables and concepts are tied together in this module,
    which makes it a bit larger than most. Additionally there are many layers
    at work for things, especially for Host, Service Instance, and Map. The
    reason for this is that breaking each component down into seperate tables
    yields higher numbers of tables, but with FAR less nullable columns, which
    simultaneously increases the density of information per row (and speedy
    table scans where they're required) but increases the 'thruthiness'[1] of
    every row. (Daqscott 4/13/08)

    [1] http://en.wikipedia.org/wiki/Truthiness """

from datetime import datetime

from sqlalchemy import (Column, Integer, Sequence, String, DateTime, Boolean,
                        ForeignKey, PrimaryKeyConstraint)
from sqlalchemy.orm import relation, backref, deferred, aliased, object_session
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import or_, null
from sqlalchemy.util import memoized_property

from aquilon.aqdb.column_types.aqstr import AqStr
from aquilon.aqdb.model import (Base, Archetype, Personality, PersonalityStage,
                                OperatingSystem, HostEnvironment)

_TN = 'service'
_SLI = 'service_list_item'
_PSLI = 'personality_service_list_item'
_OSLI = 'os_service_list_item'


class Service(Base):
    """ SERVICE: composed of a simple name of a service consumable by
        OTHER hosts. Applications that run on a system like ssh are
        personalities or features, not services. """

    __tablename__ = _TN

    id = Column(Integer, Sequence('%s_id_seq' % _TN), primary_key=True)
    name = Column(AqStr(64), nullable=False, unique=True)
    max_clients = Column(Integer, nullable=True)  # 0 means 'no limit'
    need_client_list = Column(Boolean, nullable=False, default=False)
    creation_date = deferred(Column(DateTime, default=datetime.now,
                                    nullable=False))
    allow_alias_bindings = Column(Boolean, default=False, nullable=False)
    comments = Column(String(255), nullable=True)

    __table_args__ = ({'info': {'unique_fields': ['name']}},)

    def __init__(self, name=None, **kwargs):
        name = AqStr.normalize(name)
        super(Service, self).__init__(name=name, **kwargs)

    @memoized_property
    def cluster_aligned_personalities(self):
        session = object_session(self)

        PersService = aliased(Service)
        ArchService = aliased(Service)

        # Check if the service instance is used by any cluster-bound personality
        q = session.query(PersonalityStage.id)
        q = q.outerjoin(PersonalityServiceListItem)
        q = q.outerjoin(PersService, PersonalityServiceListItem.service)
        q = q.reset_joinpoint()
        q = q.join(Personality, Archetype)
        q = q.filter(Archetype.cluster_type != null())
        q = q.outerjoin(ArchService, Archetype.required_services)
        q = q.filter(or_(PersService.id == self.id, ArchService.id == self.id))
        q = q.distinct()
        return [persst.id for persst in q]


class __ServiceListItem(Base):
    """ Service list item is an individual member of a service list, defined
        in configuration. They represent requirements for baseline archetype
        builds. Think of things like 'dns', 'syslog', etc. that you'd need just
        to get a host up and running...that's what these represent. """

    __tablename__ = _SLI
    _class_label = 'Required Service'

    service_id = Column(ForeignKey(Service.id), nullable=False)

    archetype_id = Column(ForeignKey(Archetype.id, ondelete='CASCADE'),
                          nullable=False, index=True)

    __table_args__ = (PrimaryKeyConstraint(service_id, archetype_id),)

Service.archetypes = relation(Archetype, secondary=__ServiceListItem.__table__,
                              backref=backref("required_services",
                                              passive_deletes=True))


class PersonalityServiceListItem(Base):
    """ A personality service list item is an individual member of a list
       of required services for a given personality. They represent required
       services that need to be assigned/selected in order to build
       hosts in said personality """

    __tablename__ = _PSLI

    service_id = Column(ForeignKey(Service.id), nullable=False)

    personality_stage_id = Column(ForeignKey(PersonalityStage.id,
                                             ondelete='CASCADE'),
                                  nullable=False, index=True)

    host_environment_id = Column(ForeignKey(HostEnvironment.id), nullable=True)

    service = relation(Service, innerjoin=True,
                       backref=backref("personality_assignments"))

    personality_stage = relation(PersonalityStage, innerjoin=True,
                                 backref=backref("required_services",
                                                 collection_class=attribute_mapped_collection('service'),
                                                 cascade="all, delete-orphan",
                                                 passive_deletes=True))

    host_environment = relation(HostEnvironment)

    __table_args__ = (PrimaryKeyConstraint(service_id, personality_stage_id),)

    def copy(self):
        return type(self)(service=self.service,
                          host_environment=self.host_environment)


class __OSServiceListItem(Base):
    __tablename__ = _OSLI

    service_id = Column(ForeignKey(Service.id), nullable=False)

    operating_system_id = Column(ForeignKey(OperatingSystem.id,
                                            ondelete='CASCADE'),
                                 nullable=False, index=True)

    __table_args__ = (PrimaryKeyConstraint(service_id, operating_system_id),)

Service.operating_systems = relation(OperatingSystem,
                                     secondary=__OSServiceListItem.__table__,
                                     backref=backref("required_services",
                                                     passive_deletes=True))
