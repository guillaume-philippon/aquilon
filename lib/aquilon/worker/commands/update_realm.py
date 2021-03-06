# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2012,2014,2016  Contributor
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

from aquilon.worker.broker import BrokerCommand
from aquilon.aqdb.model import Realm


class CommandUpdateRealm(BrokerCommand):

    required_parameters = ["realm"]

    def render(self, session, realm, trusted, comments, **_):
        dbrealm = Realm.get_unique(session, realm, compel=True)

        if trusted is not None:
            dbrealm.trusted = trusted
        if comments is not None:
            dbrealm.comments = comments

        session.flush()

        return
