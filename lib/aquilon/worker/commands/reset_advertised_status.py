# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2015,2016  Contributor
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
"""Contains the logic for `aq reset advertised status --hostname`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.host import hostname_to_host
from aquilon.worker.templates import TemplateDomain


class CommandResetAdvertisedStatus(BrokerCommand):
    requires_plenaries = True
    """ reset advertised status for single host """

    required_parameters = ["hostname"]

    def render(self, session, logger, plenaries, hostname, **_):
        dbhost = hostname_to_host(session, hostname)
        if dbhost.status.name == 'ready':
            raise ArgumentError("{0:l} is in ready status, "
                                "advertised status can be reset only "
                                "when host is in non ready state."
                                .format(dbhost))

        dbhost.advertise_status = False

        session.flush()

        td = TemplateDomain(dbhost.branch, dbhost.sandbox_author, logger=logger)
        plenaries.add(dbhost, allow_incomplete=False)
        # Force a host lock as pan might overwrite the profile...
        with plenaries.transaction():
            td.compile(session, only=plenaries.object_templates)

        return
