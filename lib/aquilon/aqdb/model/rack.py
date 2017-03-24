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
""" Rack is a subclass of Location """

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import validates

from aquilon.aqdb.column_types import AqStr
from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Location, Building, Room, Bunker


class Rack(Location):
    """ Rack is a subtype of location """
    __tablename__ = 'rack'
    __mapper_args__ = {'polymorphic_identity': 'rack'}

    valid_parents = [Building, Room, Bunker]

    id = Column(ForeignKey(Location.id, ondelete='CASCADE'), primary_key=True)

    rack_row = Column(AqStr(4), nullable=True)
    rack_column = Column(AqStr(4), nullable=True)

    __table_args__ = ({'info': {'unique_fields': ['name']}},)

    @validates('rack_row', 'rack_column')
    def check_rack_coordinates(self, key, value):
        """ validates the row and column arguments """
        value = str(value).strip()
        if not value.isalnum():
            msg = "the value '%s' for %s must be alphanumeric" % (
                value, key)
            raise ArgumentError(msg)
        else:
            return value
