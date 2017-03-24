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
"""The tables/objects/mappings related to hardware in Aquilon. """

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relation

from aquilon.aqdb.column_types import GUID
from aquilon.aqdb.model import Model, HardwareEntity


class Machine(HardwareEntity):
    """ Machines represents general purpose computers """

    __tablename__ = 'machine'
    __mapper_args__ = {'polymorphic_identity': 'machine'}

    hardware_entity_id = Column(ForeignKey(HardwareEntity.id,
                                           ondelete='CASCADE'),
                                primary_key=True)

    cpu_model_id = Column(ForeignKey(Model.id, name='machine_cpu_model_fk'),
                          nullable=False, index=True)

    # TODO: constrain/smallint
    cpu_quantity = Column(Integer, nullable=False, default=2)

    memory = Column(Integer, nullable=False, default=512)

    uuid = Column(GUID, nullable=True, unique=True)

    uri = Column(String(400), nullable=True)

    cpu_model = relation(Model, innerjoin=True, foreign_keys=cpu_model_id)

    @property
    def cluster(self):
        # Bound to a cluster
        if self.vm_container and hasattr(self.vm_container.holder, 'cluster'):
            return self.vm_container.holder.holder_object
        # Vulcan local disk with esx cluster
        if self.vm_container and hasattr(self.vm_container.holder, 'host') and hasattr(self.vm_container.holder.host, 'cluster'):
            return self.vm_container.holder.host.cluster
        else:
            return None

# TODO: an __init__ (or other method) that could use DSDB to create itself?
# check if it exists in dbdb minfo, and get from there if it does
# and/or -dsdb option, and, make machine --like [other machine] + overrides

# TODO: an __init__ that uses the machine specs to dynamically populate default
# values for all of the attrs where its possible
