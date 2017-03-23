# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2013,2014,2015,2016  Contributor
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
"""Contains the logic for `aq update share`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Share
from aquilon.utils import validate_nlist_key
from aquilon.worker.broker import BrokerCommand


class CommandUpdateShare(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["share"]

    def render(self, session, plenaries, share, latency_threshold,
               comments, **_):

        validate_nlist_key("share", share)

        q = session.query(Share).filter_by(name=share)

        if not q.count():
            raise ArgumentError("Share %s is not used on any resource and "
                                "cannot be modified" % share)

        for dbshare in q:
            if latency_threshold:
                dbshare.latency_threshold = latency_threshold

            if comments is not None:
                dbshare.comments = comments

            plenaries.add(dbshare)

        session.flush()
        plenaries.write()

        return
