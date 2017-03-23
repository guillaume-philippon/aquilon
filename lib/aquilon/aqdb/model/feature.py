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
""" Control of features """

from collections import defaultdict
from datetime import datetime

from six import iteritems

from sqlalchemy import (Column, Integer, DateTime, Sequence, String, Boolean,
                        ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relation, backref, deferred, validates
from sqlalchemy.orm.exc import NoResultFound

from aquilon.exceptions_ import ArgumentError, NotFoundException, InternalError
from aquilon.aqdb.model import Base, Archetype, PersonalityStage, Model, Grn
from aquilon.aqdb.column_types import AqStr, Enum
from aquilon.aqdb.model.base import _raise_custom

_TN = 'feature'
_LINK = 'feature_link'

_VISIBILITY = ('public', 'restricted', 'owner_approved', 'owner_only', 'legacy')
_ACTIVATION_TYPE = ('rebuild', 'reboot', 'dispatch')


class Feature(Base):
    __tablename__ = _TN

    post_personality_allowed = False

    id = Column(Integer, Sequence("%s_id_seq" % _TN), primary_key=True)
    name = Column(String(128), nullable=False)
    feature_type = Column(AqStr(16), nullable=False)
    post_personality = Column(Boolean, nullable=False, default=False)
    owner_eon_id = Column(ForeignKey(Grn.eon_id, name='%s_owner_grn_fk' % _TN),
                          nullable=False)
    visibility = Column(Enum(16, _VISIBILITY), nullable=False)
    activation = Column(Enum(10, _ACTIVATION_TYPE), nullable=True)
    deactivation = Column(Enum(10, _ACTIVATION_TYPE), nullable=True)
    creation_date = deferred(Column(DateTime, default=datetime.now,
                                    nullable=False))
    comments = deferred(Column(String(255), nullable=True))

    owner_grn = relation(Grn, innerjoin=True)

    __table_args__ = (UniqueConstraint(name, feature_type),
                      {'info': {'unique_fields': ['name', 'feature_type']}},)

    __mapper_args__ = {'polymorphic_on': feature_type}

    @validates('links')
    def _validate_link(self, key, link):
        # Due to how decorators work, we have to do a level of indirection to
        # make polymorphism work
        return self.validate_link(key, link)

    # pylint: disable=W0613
    def validate_link(self, key, link):  # pragma: no cover
        return link

    @validates('visibility')
    def validate_visibility(self, key, visibility):
        """ Utility function for validating the value type """
        if not visibility:
            return
        if visibility in _VISIBILITY:
            return visibility
        valid_visibility = ", ".join(sorted(_VISIBILITY))
        raise ArgumentError("Unknown value for %s. Valid values are: "
                            "%s." % (key, valid_visibility))

    @validates('activation')
    def validate_activation(self, key, activation):
        """ Utility function for validating the value type """
        if not activation:
            return
        if activation in _ACTIVATION_TYPE:
            return activation
        valid_activation = ", ".join(sorted(_ACTIVATION_TYPE))
        raise ArgumentError("Unknown value for %s. Valid values are: "
                            "%s." % (key, valid_activation))

    @validates('deactivation')
    def validate_deactivation(self, key, deactivation):
        return self.validate_activation(key, deactivation)


class HostFeature(Feature):
    _class_label = "Host Feature"

    __mapper_args__ = {'polymorphic_identity': 'host'}

    post_personality_allowed = True

    @property
    def cfg_path(self):
        return "features/%s" % self.name

    def validate_link(self, key, link):
        if link.model:
            raise InternalError("Host features can not be bound to "
                                "hardware models.")
        return link

    def __init__(self, name=None, **kwargs):
        if not name:  # pragma: no cover
            raise ValueError("The name is a required property for a feature.")

        if name.startswith("hardware/") or name.startswith("interface/"):
            raise ArgumentError("The 'hardware/' and 'interface/' prefixes "
                                "are not available for host features.")

        super(HostFeature, self).__init__(name=name, **kwargs)


class HardwareFeature(Feature):
    _class_label = "Hardware Feature"

    __mapper_args__ = {'polymorphic_identity': 'hardware'}

    @property
    def cfg_path(self):
        return "features/hardware/%s" % self.name

    def validate_link(self, key, link):
        if not link.model or not link.model.model_type.isHardwareEntityType():
            raise InternalError("Hardware features can only be bound to "
                                "machine models.")
        return link


class InterfaceFeature(Feature):
    _class_label = "Interface Feature"

    __mapper_args__ = {'polymorphic_identity': 'interface'}

    @property
    def cfg_path(self):
        return "features/interface/%s" % self.name

    def validate_link(self, key, link):
        if (link.model and link.model.model_type.isNic()) or \
           (link.interface_name and link.personality_stage):
            return link

        raise InternalError("Interface features can only be bound to "
                            "NIC models or personality/interface name pairs.")


def _error_msg(archetype, personality_stage, model, interface_name):
    msg = []
    if archetype or personality_stage:
        msg.append("{0:l}".format(archetype or personality_stage))
    if model:
        msg.append(format(model, "l"))
    if interface_name:
        msg.append("interface %s" % interface_name)
    return ", ".join(msg)


class FeatureLink(Base):
    __tablename__ = _LINK

    id = Column(Integer, Sequence("%s_id_seq" % _LINK), primary_key=True)

    feature_id = Column(ForeignKey(Feature.id), nullable=False)

    model_id = Column(ForeignKey(Model.id, ondelete='CASCADE'),
                      nullable=True, index=True)

    archetype_id = Column(ForeignKey(Archetype.id, ondelete='CASCADE'),
                          nullable=True, index=True)

    personality_stage_id = Column(ForeignKey(PersonalityStage.id,
                                             ondelete='CASCADE'),
                                  nullable=True, index=True)

    interface_name = Column(AqStr(32), nullable=True)

    creation_date = deferred(Column(DateTime, default=datetime.now,
                                    nullable=False))

    feature = relation(Feature, innerjoin=True,
                       backref=backref('links', passive_deletes=True))

    model = relation(Model,
                     backref=backref('features', passive_deletes=True))

    archetype = relation(Archetype,
                         backref=backref('features', passive_deletes=True))

    personality_stage = relation(PersonalityStage,
                                 backref=backref('features',
                                                 passive_deletes=True))

    # The behavior of UNIQUE constraints in the presence of NULL columns is not
    # universal. We need the Oracle compatible behavior, meaning:
    # - Trying to add a row like ('a', NULL) two times should fail
    # - Trying to add ('b', NULL) after ('a', NULL) should succeed
    __table_args__ = (UniqueConstraint(feature_id, model_id, archetype_id,
                                       personality_stage_id, interface_name,
                                       name='%s_uk' % _LINK),)

    def __init__(self, feature=None, archetype=None, personality_stage=None,
                 model=None, interface_name=None):
        # Archetype and personality are mutually exclusive. This makes
        # querying archetype-wide features a bit easier
        if archetype and personality_stage:  # pragma: no cover
            raise InternalError("Archetype and personality are mutually "
                                "exclusive.")

        if interface_name and not personality_stage:  # pragma: no cover
            raise InternalError("Binding to a named interface requires "
                                "a personality.")

        super(FeatureLink, self).__init__(feature=feature, archetype=archetype,
                                          personality_stage=personality_stage,
                                          model=model,
                                          interface_name=interface_name)

    @classmethod
    def get_unique(cls, session, feature=None, archetype=None,
                   personality_stage=None, model=None, interface_name=None,
                   compel=False, preclude=False):
        if feature is None:  # pragma: no cover
            raise ValueError("Feature must be specified.")

        q = session.query(cls)
        q = q.filter_by(feature=feature, archetype=archetype,
                        personality_stage=personality_stage, model=model,
                        interface_name=interface_name)
        try:
            result = q.one()
            if preclude:
                msg = "{0} is already bound to {1}.".format(
                    feature, _error_msg(archetype, personality_stage, model,
                                        interface_name))
                _raise_custom(preclude, ArgumentError, msg)
        except NoResultFound:
            if not compel:
                return None
            msg = "{0} is not bound to {1}.".format(
                feature, _error_msg(archetype, personality_stage, model,
                                    interface_name))
            _raise_custom(compel, NotFoundException, msg)

        return result

    def copy(self):
        return type(self)(feature=self.feature, model=self.model,
                          personality_stage=self.personality_stage,
                          archetype=self.archetype,
                          interface_name=self.interface_name)


def hardware_features(dbstage, dbmodel):
    features = set()

    for link in dbstage.features + dbstage.archetype.features:
        if not isinstance(link.feature, HardwareFeature):
            continue
        if link.model != dbmodel:
            continue

        features.add(link.feature)

    return frozenset(features)


def host_features(dbstage):
    pre = set()
    post = set()
    for link in dbstage.features + dbstage.archetype.features:
        if not isinstance(link.feature, HostFeature):
            continue

        if link.feature.post_personality:
            post.add(link.feature)
        else:
            pre.add(link.feature)

    return (frozenset(pre), frozenset(post))


def interface_features(dbstage, dbinterface):
    features = set()

    for link in dbstage.features + dbstage.archetype.features:
        if not isinstance(link.feature, InterfaceFeature):
            continue
        if link.interface_name and link.interface_name != dbinterface.name:
            continue
        if link.model and link.model != dbinterface.model:
            continue

        features.add(link.feature)

    return frozenset(features)


def nonhost_features(dbstage, dbhw_ent):
    # A slightly optimized version to collect all hardware and interface
    # features while enumerating the links just once
    hw_features = set()
    iface_features = defaultdict(set)

    for link in dbstage.features + dbstage.archetype.features:
        if isinstance(link.feature, HardwareFeature):
            if link.model == dbhw_ent.model:
                hw_features.add(link.feature)
        elif isinstance(link.feature, InterfaceFeature):
            for dbinterface in dbhw_ent.interfaces:
                if link.model and link.model != dbinterface.model:
                    continue
                if link.interface_name and link.interface_name != dbinterface.name:
                    continue
                iface_features[dbinterface].add(link.feature)

        else:
            pass

    for key, value in iteritems(iface_features):
        iface_features[key] = frozenset(value)

    return frozenset(hw_features), iface_features
