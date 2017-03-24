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
"""Contains the logic for `aq add model`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.types import CpuType, NicType
from aquilon.aqdb.model import Vendor, Model, MachineSpecs
from aquilon.worker.broker import BrokerCommand


class CommandAddModel(BrokerCommand):

    required_parameters = ["model", "vendor", "type"]

    def render(self, session, model, vendor, type, cpuname, cpuvendor,
               cpunum, memory, disktype, diskcontroller, disksize,
               nicmodel, nicvendor, comments, **_):
        dbvendor = Vendor.get_unique(session, vendor, compel=True)
        Model.get_unique(session, name=model, vendor=dbvendor, preclude=True)

        # Specifically not allowing new models to be added that are of
        # type aurora_node - that is only meant for the dummy aurora_model.
        if type.isAuroraChassis() or type.isAuroraNode():
            raise ArgumentError("The model's machine type must not be"
                                " an aurora type")

        dbmodel = Model(name=model, vendor=dbvendor, model_type=type,
                        comments=comments)
        session.add(dbmodel)
        session.flush()

        if cpuname or cpuvendor:
            if not type.isMachineType():
                raise ArgumentError("Machine specfications are only valid"
                                    " for machine types")
            dbcpu = Model.get_unique(session, model_type=CpuType.Cpu,
                                     name=cpuname, vendor=cpuvendor,
                                     compel=True)
            if nicmodel or nicvendor:
                dbnic = Model.get_unique(session, model_type=NicType.Nic,
                                         name=nicmodel, vendor=nicvendor,
                                         compel=True)
            else:
                dbnic = Model.default_nic_model(session)
            dbmachine_specs = MachineSpecs(model=dbmodel, cpu_model=dbcpu,
                                           cpu_quantity=cpunum, memory=memory,
                                           disk_type=disktype,
                                           controller_type=diskcontroller,
                                           disk_capacity=disksize,
                                           nic_model=dbnic)
            session.add(dbmachine_specs)
        return
