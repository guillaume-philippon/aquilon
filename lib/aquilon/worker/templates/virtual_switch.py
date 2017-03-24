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

import logging
from operator import attrgetter

from sqlalchemy.inspection import inspect

from aquilon.aqdb.model import VirtualSwitch
from aquilon.worker.locks import NoLockKey, PlenaryKey
from aquilon.worker.templates import Plenary, StructurePlenary
from aquilon.worker.templates.panutils import pan_assign


LOGGER = logging.getLogger(__name__)


class PlenaryVirtualSwitchData(StructurePlenary):
    prefix = "virtualswitchdata"

    @classmethod
    def template_name(cls, dbvswitch):
        return cls.prefix + "/" + dbvswitch.name

    def get_key(self, exclusive=True):
        if inspect(self.dbobj).deleted:
            return NoLockKey(logger=self.logger)
        else:
            return PlenaryKey(virtual_switch=self.dbobj, logger=self.logger,
                              exclusive=exclusive)

    def body(self, lines):
        for pg in sorted(self.dbobj.port_groups,
                         key=attrgetter("usage", "network_tag")):
            params = {"network_tag": pg.network_tag,
                      "network_ip": pg.network.ip,
                      "usage": pg.usage,

                      "netmask": pg.network.netmask,
                      "network_type": pg.network.network_type,
                      "network_environment": pg.network.network_environment}
            pan_assign(lines, "system/virtual_switch/port_groups/{%s}" % pg.name, params)

Plenary.handlers[VirtualSwitch] = PlenaryVirtualSwitchData
