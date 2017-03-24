# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2016  Contributor
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
"""Contains the logic for `aq del network_environment`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import NetworkEnvironment, Network
from aquilon.worker.broker import BrokerCommand


class CommandDelNetworkEnvironment(BrokerCommand):

    required_parameters = ["network_environment"]

    def render(self, session, network_environment, **_):
        dbnet_env = NetworkEnvironment.get_unique(session, network_environment,
                                                  compel=True)

        if dbnet_env.is_default:
            raise ArgumentError("{0} is the default network environment, "
                                "therefore it cannot be deleted."
                                .format(dbnet_env))
        if session.query(Network).filter_by(network_environment=dbnet_env).first():
            raise ArgumentError("{0} still has networks defined, delete them "
                                "first.".format(dbnet_env))
        session.delete(dbnet_env)
        session.flush()
        return
