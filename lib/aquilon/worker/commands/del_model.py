# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2015,2016  Contributor
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
"""Contains the logic for `aq del model`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand
from aquilon.aqdb.model import (Vendor, Model, MachineSpecs, HardwareEntity,
                                Machine, Interface)


class CommandDelModel(BrokerCommand):

    required_parameters = ["model", "vendor"]
    model_type = None

    def render(self, session, logger, model, vendor, **_):
        dbvendor = Vendor.get_unique(session, vendor, compel=True)
        dbmodel = Model.get_unique(session, name=model, vendor=dbvendor,
                                   model_type=self.model_type, compel=True)

        if dbmodel.model_type.isNic():
            q = session.query(Interface.id)
            q = q.filter_by(model=dbmodel)
            if q.count():
                raise ArgumentError("{0} is still in use and cannot be "
                                    "deleted.".format(dbmodel))
            q = session.query(MachineSpecs.id)
            q = q.filter_by(nic_model=dbmodel)
            if q.count():
                raise ArgumentError("{0} is still referenced by machine models and "
                                    "cannot be deleted.".format(dbmodel))
        if dbmodel.model_type.isCpu():
            q = session.query(Machine.hardware_entity_id)
            q = q.filter_by(cpu_model=dbmodel)
            if q.count():
                raise ArgumentError("{0} is still in use and cannot be "
                                    "deleted.".format(dbmodel))

            q = session.query(MachineSpecs.id)
            q = q.filter_by(cpu_model=dbmodel)
            if q.count():
                raise ArgumentError("{0} is still referenced by machine models and "
                                    "cannot be deleted.".format(dbmodel))
        else:
            q = session.query(HardwareEntity.id)
            q = q.filter_by(model=dbmodel)
            if q.count():
                raise ArgumentError("{0} is still in use and cannot be "
                                    "deleted.".format(dbmodel))

        if dbmodel.machine_specs:
            # FIXME: Log some details...
            logger.info("Before deleting model %s %s '%s', "
                        "removing machine specifications." %
                        (dbmodel.model_type, dbvendor.name, dbmodel.name))
            session.delete(dbmodel.machine_specs)

        session.delete(dbmodel)
        session.flush()

        return
