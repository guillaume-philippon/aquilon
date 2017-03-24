# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013,2014,2015,2016  Contributor
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

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation, backref

from aquilon.exceptions_ import ArgumentError, AquilonError
from aquilon.aqdb.column_types.aqstr import AqStr
from aquilon.aqdb.model import Resource, ResourceHolder


_TN = 'resourcegroup'
_RESHOLDER = 'resholder'


class ResourceGroup(Resource):
    """ A collection of resources which operate together
        (e.g. a VCS Service Group)."""
    __tablename__ = _TN
    _class_label = 'Resource Group'

    resource_id = Column(ForeignKey(Resource.id, ondelete='CASCADE'),
                         primary_key=True)

    # declare any per-group attributes here (none for now)

    # This is to enforce the same type of resources in the group
    required_type = Column(AqStr(32), nullable=True)

    __table_args__ = ({'info': {'unique_fields': ['name', 'holder']}},)
    __mapper_args__ = {'polymorphic_identity': _TN}

    def validate_holder(self, key, value):
        if isinstance(value, BundleResource):
            raise AquilonError("ResourceGroups must not be held by other "
                               "ResourceGroups")
        return value


class BundleResource(ResourceHolder):
    '''Allow ResourceGroups to hold other types of resource. '''

    resourcegroup_id = Column(ForeignKey(ResourceGroup.resource_id,
                                         name='%s_bundle_fk' % _RESHOLDER,
                                         ondelete='CASCADE',
                                         deferrable=True,
                                         initially='IMMEDIATE',
                                         use_alter=True),
                              nullable=True, unique=True)

    # This is a one-to-one relation, so we need uselist=False on the backref
    resourcegroup = relation(ResourceGroup, lazy='subquery',
                             foreign_keys=resourcegroup_id,
                             backref=backref('resholder',
                                             cascade='all, delete-orphan',
                                             uselist=False))

    # Note: the polymorphic identity of ResourceGroup and BundleResource should
    # be the same, because plenary paths sometimes use one or the other,
    # depending on the context. These two classes should really be one if there
    # was a sane way to support multiple inheritance in the DB, so their
    # identities should at least be the same.
    __mapper_args__ = {'polymorphic_identity': _TN}

    def validate_resources(self, key, value):
        rg = self.resourcegroup
        if rg.required_type and rg.required_type != value.resource_type:
            raise ArgumentError("{0} may contain resources of type {1!s} only."
                                .format(self, rg.required_type))

        return value

    @property
    def holder_name(self):
        return self.resourcegroup.name

    @property
    def holder_object(self):
        return self.resourcegroup

    @property
    def toplevel_holder_object(self):
        return self.resourcegroup.holder.holder_object
