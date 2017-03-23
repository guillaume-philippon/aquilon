# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2014,2016  Contributor
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
""" Contains the logic of "aq refresh user_principal" """

from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.user import UserSync
from aquilon.worker.locks import SyncKey


class CommandRefreshUser(BrokerCommand):
    requires_plenaries = True

    def render(self, session, logger, plenaries, incremental, ignore_delete_limit, **_):
        with SyncKey(data="user", logger=logger):
            sync = UserSync(self.config, session, logger, plenaries,
                            incremental, ignore_delete_limit)
            sync.refresh_user()

        return
