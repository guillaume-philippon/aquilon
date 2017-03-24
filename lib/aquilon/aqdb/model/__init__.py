# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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

import aquilon.aqdb.depends

from aquilon.aqdb.model.base import Base, SingleInstanceMixin
from aquilon.aqdb.model.stateengine import StateEngine
from aquilon.aqdb.model.lifecycleengine import LifecycleEngine

# AUTHORIZATION
from aquilon.aqdb.model.role import Role
from aquilon.aqdb.model.realm import Realm
from aquilon.aqdb.model.user_principal import UserPrincipal
from aquilon.aqdb.model.user import User
from aquilon.aqdb.model.netgroup_whitelist import NetGroupWhiteList

# DNS DOMAINS
from aquilon.aqdb.model.dns_domain import DnsDomain

# LOCATION
from aquilon.aqdb.model.location import Location
from aquilon.aqdb.model.organization import Organization
from aquilon.aqdb.model.hub import Hub
from aquilon.aqdb.model.continent import Continent
from aquilon.aqdb.model.country import Country
from aquilon.aqdb.model.campus import Campus
from aquilon.aqdb.model.city import City
from aquilon.aqdb.model.building import Building
from aquilon.aqdb.model.room import Room
from aquilon.aqdb.model.bunker import Bunker
from aquilon.aqdb.model.rack import Rack
from aquilon.aqdb.model.desk import Desk

# GRN
from aquilon.aqdb.model.grn import Grn

# NETWORK
from aquilon.aqdb.model.dns_environment import DnsEnvironment
from aquilon.aqdb.model.network_environment import NetworkEnvironment
from aquilon.aqdb.model.network_compartment import NetworkCompartment
from aquilon.aqdb.model.network import Network
from aquilon.aqdb.model.static_route import StaticRoute
from aquilon.aqdb.model.fqdn import Fqdn
from aquilon.aqdb.model.dns_record import DnsRecord
from aquilon.aqdb.model.dns_record_target_mixin import DnsRecordTargetMixin
from aquilon.aqdb.model.a_record import ARecord, DynamicStub
from aquilon.aqdb.model.reserved_name import ReservedName
from aquilon.aqdb.model.address_alias import AddressAlias
from aquilon.aqdb.model.alias import Alias
from aquilon.aqdb.model.srv_record import SrvRecord
from aquilon.aqdb.model.ns_record import NsRecord
from aquilon.aqdb.model.router_address import RouterAddress

# CONFIG
from aquilon.aqdb.model.archetype import Archetype
from aquilon.aqdb.model.host_environment import HostEnvironment
from aquilon.aqdb.model.personality import (Personality, PersonalityGrnMap,
                                            PersonalityStage)
from aquilon.aqdb.model.asset_lifecycle import AssetLifecycle
from aquilon.aqdb.model.operating_system import OperatingSystem

# HARDWARE
from aquilon.aqdb.model.vendor import Vendor
from aquilon.aqdb.model.model import Model
from aquilon.aqdb.model.hardware_entity import HardwareEntity, DeviceLinkMixin
from aquilon.aqdb.model.machine import Machine
from aquilon.aqdb.model.hostlifecycle import HostLifecycle
from aquilon.aqdb.model.network_device import NetworkDevice
from aquilon.aqdb.model.chassis import Chassis
from aquilon.aqdb.model.disk import Disk, LocalDisk
from aquilon.aqdb.model.machine_specs import MachineSpecs

# HOST
from aquilon.aqdb.model.branch import Branch, Domain, Sandbox, Review
from aquilon.aqdb.model.compileable import CompileableMixin
from aquilon.aqdb.model.host import Host, HostGrnMap

# HARDWARE/SYSTEM LINKAGES
from aquilon.aqdb.model.observed_mac import ObservedMac
from aquilon.aqdb.model.chassis_slot import ChassisSlot
from aquilon.aqdb.model.vlan import PortGroup, VlanInfo
from aquilon.aqdb.model.interface import (Interface, PublicInterface,
                                          ManagementInterface, OnboardInterface,
                                          VlanInterface, BondingInterface,
                                          BridgeInterface, LoopbackInterface,
                                          VirtualInterface, PhysicalInterface)
from aquilon.aqdb.model.address_assignment import (AddressAssignment,
                                                   SharedAddressAssignment)

# FEATURES
from aquilon.aqdb.model.feature import (Feature, FeatureLink, HostFeature,
                                        HardwareFeature, InterfaceFeature)
from aquilon.aqdb.model.parameter_definition import (ParamDefinition, ParamDefHolder,
                                                     ArchetypeParamDef, FeatureParamDef)
from aquilon.aqdb.model.parameter import Parameter, PersonalityParameter

# CLUSTER
from aquilon.aqdb.model.clusterlifecycle import ClusterLifecycle
from aquilon.aqdb.model.building_preference import BuildingPreference
from aquilon.aqdb.model.cluster import (Cluster, HostClusterMember, EsxCluster,
                                        ComputeCluster, StorageCluster)
from aquilon.aqdb.model.personality_cluster_info import (PersonalityClusterInfo,
                                                         PersonalityESXClusterInfo)
from aquilon.aqdb.model.cluster_group import ClusterGroup

from aquilon.aqdb.model.virtual_switch import VirtualSwitch
from aquilon.aqdb.model.metacluster import MetaCluster

# SERVICE
from aquilon.aqdb.model.service import Service, PersonalityServiceListItem
from aquilon.aqdb.model.service_instance import ServiceInstance
from aquilon.aqdb.model.service_map import ServiceMap

from aquilon.aqdb.model.xtn import Xtn, XtnDetail, XtnEnd

# Resources
from aquilon.aqdb.model.resource import (Resource, ResourceHolder,
                                         HostResource, ClusterResource)
from aquilon.aqdb.model.filesystem import Filesystem
from aquilon.aqdb.model.application import Application
from aquilon.aqdb.model.hostlink import Hostlink
from aquilon.aqdb.model.intervention import Intervention
from aquilon.aqdb.model.resourcegroup import ResourceGroup, BundleResource
from aquilon.aqdb.model.reboot_schedule import (RebootSchedule,
                                                RebootIntervention)

from aquilon.aqdb.model.virtual_machine import VirtualMachine
from aquilon.aqdb.model.service_address import ServiceAddress
from aquilon.aqdb.model.share import Share
from aquilon.aqdb.model.virtual_disk import VirtualDisk
from aquilon.aqdb.model.cluster_asl import (PriorityList, MemberPriority,
                                            SystemList, AutoStartList)

from aquilon.aqdb.model.service_instance_server import ServiceInstanceServer
