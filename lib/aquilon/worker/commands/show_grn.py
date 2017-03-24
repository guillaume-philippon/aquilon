# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2016  Contributor
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
"""Contains the logic for `aq show grn`."""

from aquilon.exceptions_ import NotFoundException
from aquilon.aqdb.model import Grn
from aquilon.worker.broker import BrokerCommand


class CommandShowGrn(BrokerCommand):

    def render(self, session, grn, eon_id, all, **_):
        q = session.query(Grn)
        if grn:
            q = q.filter_by(grn=grn)
        if eon_id:
            q = q.filter_by(eon_id=eon_id)
        result = q.all()
        if not result:
            if grn:
                raise NotFoundException("GRN %s not found." % grn)
            elif eon_id:
                raise NotFoundException("EON ID %s not found." % eon_id)
        return result
