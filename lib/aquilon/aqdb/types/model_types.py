# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2015  Contributor
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

from aquilon.aqdb.types import StringEnum


class ModelType(StringEnum):
    pass


class HardwareEntityType(ModelType):
    pass


class MachineType(HardwareEntityType):
    pass


class PhysicalMachineType(MachineType):
    Blade = 'blade'
    Rackmount = 'rackmount'
    Workstation = 'workstation'
    AuroraNode = 'aurora_node'


class VirtualMachineType(MachineType):
    VirtualMachine = 'virtual_machine'
    VirtualAppliance = 'virtual_appliance'


class ChassisType(HardwareEntityType):
    Chassis = 'chassis'
    AuroraChassis = 'aurora_chassis'


class NetworkDeviceType(HardwareEntityType):
    Switch = 'switch'
    Router = 'router'
    SwitchRouter = 'switch-router'
    WirelessAP = 'wireless-ap'
    WirelessController = 'wireless-controller'
    LoadBalancer = 'load-balancer'
    NetworkAppliance = 'network-appliance'


class NicType(ModelType):
    Nic = 'nic'


class CpuType(ModelType):
    Cpu = 'cpu'
