# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014  Contributor
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
""" Network Devices """
from datetime import datetime

from sqlalchemy import Column, ForeignKey, DateTime

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import HardwareEntity
from aquilon.aqdb.column_types import Enum

SWITCH_TYPES = ('tor', 'bor', 'agg', 'misc')
_TN = 'network_device'


class NetworkDevice(HardwareEntity):
    __tablename__ = _TN
    _class_label = 'Switch'
    __mapper_args__ = {'polymorphic_identity': _TN}

    hardware_entity_id = Column(ForeignKey(HardwareEntity.id,
                                           ondelete='CASCADE'),
                                primary_key=True)

    switch_type = Column(Enum(16, SWITCH_TYPES), nullable=False)

    last_poll = Column(DateTime, nullable=False, default=datetime.now)

    @classmethod
    def check_type(cls, type):
        if type is not None and type not in SWITCH_TYPES:
            raise ArgumentError("Unknown switch type '%s'." % type)
