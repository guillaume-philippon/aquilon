#!/usr/bin/env python
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
"""
    This module produces some HTML docuemation of the the database model.
    It does so by inspecting the database module to produce a set of
    diagrams.  For each of the classes in the diagrams we add the
    documenation contained in the source iself.
"""

###############################################################################

import argparse
import os
import sys

_DIR = os.path.dirname(os.path.realpath(__file__))
_LIBDIR = os.path.join(_DIR, '..', 'lib')
sys.path.insert(0, _LIBDIR)

import aquilon.aqdb.depends

###############################################################################

parser = argparse.ArgumentParser(description='generate schema graphs')
parser.add_argument('--outputdir', '-o', dest='dir',
                    default='%s/public_html/aqdb' % os.getenv('HOME', '/tmp'),
                    help='directory to put generated files')
parser.add_argument('--prefix', '-p', dest='prefix', default='aqdb',
                    help='basename of files to generate')
opts = parser.parse_args()

if not os.path.exists(opts.dir):
    os.makedirs(opts.dir)

###############################################################################

from aquilon.config import Config, lookup_file_path

config = Config(configfile=lookup_file_path('aqd.conf.mem'))

###############################################################################

try:
    import ms.modulecmd
except ImportError:
    pass
else:
    ms.modulecmd.load("fsf/graphviz/2.6")

from aquilon.aqdb.db_factory import DbFactory
from aquilon.aqdb.model import *  # pylint: disable=W0401,W0614
from aquilon.aqdb.utils import schema2dot

from aquilon.aqdb.model.location import LocationLink
from aquilon.aqdb.model.service import (__ServiceListItem,
                                        PersonalityServiceListItem,
                                        __OSServiceListItem)
from aquilon.aqdb.model.service_instance import (__BuildItem,
                                                 __ClusterServiceBinding)
from aquilon.aqdb.model.service_address import __ServiceAddressInterface
from aquilon.aqdb.model.personality import (__PersonalityRootUser,
                                            __PersonalityRootNetGroup)
from aquilon.aqdb.model.cluster import (HostClusterMember,
                                        __ClusterAllowedPersonality)
from aquilon.aqdb.model.cluster_group import __ClusterGroupMember
from aquilon.aqdb.model.metacluster import __MetaClusterMember
from aquilon.aqdb.model.vlan import __ObservedVlan
from aquilon.aqdb.model.virtual_switch import (__VSwitchClusterAssignment,
                                               __VSwitchHostAssignment,
                                               __VSwitchPGAssignment)

from sqlalchemy import orm

###############################################################################

model_group = {
    'locations': {
        'title': 'Location Information',
        'classes': [Location, LocationLink, Organization, Hub, Continent, Country,
                    City, Campus, Building, Room, Desk, Bunker, Rack],
    },
    'hardware': {
        'title': 'Hardware Information',
        'classes': [HardwareEntity, Model, Vendor, Machine, MachineSpecs,
                    NetworkDevice, Chassis, ChassisSlot],
    },
    'resource': {
        'title': 'Resources',
        'classes': [Resource, ResourceHolder, Application, Filesystem, Hostlink,
                    Intervention, RebootIntervention, RebootSchedule,
                    ResourceGroup, ServiceAddress, __ServiceAddressInterface,
                    Share, VirtualMachine],
    },
    'host': {
        'title': 'Hosts',
        'classes': [Host, HostLifecycle, HostGrnMap, Grn,
                    OperatingSystem, AssetLifecycle,
                    VirtualSwitch, __VSwitchPGAssignment,
                    __VSwitchHostAssignment],
    },
    'personality': {
        'title': 'Personalities',
        'classes': [Personality, PersonalityStage, Archetype, HostEnvironment, Grn,
                    Parameter, PersonalityGrnMap,
                    __PersonalityRootUser, __PersonalityRootNetGroup],
    },
    'feature': {
        'title': 'Features',
        'classes': [Feature, FeatureLink, ParamDefinition, ParamDefHolder],
    },
    'services': {
        'title': 'Services',
        'classes': [Service, PersonalityServiceListItem, __ServiceListItem,
                    __OSServiceListItem, ServiceInstance, __BuildItem,
                    ServiceInstanceServer, __ClusterServiceBinding,
                    ServiceMap],
    },
    'dns': {
        'title': 'DNS',
        'classes': [DnsDomain, DnsRecord, ARecord, SrvRecord, NsRecord, Alias,
                    AddressAlias, ReservedName, Fqdn, DynamicStub,
                    DnsEnvironment],
    },
    'cluster': {
        'title': 'Clusters',
        'classes': [Cluster, EsxCluster, StorageCluster, ComputeCluster,
                    PersonalityClusterInfo, PersonalityESXClusterInfo,
                    ClusterGroup, __ClusterGroupMember,
                    HostClusterMember,
                    MetaCluster, __MetaClusterMember,
                    ClusterLifecycle, __ClusterAllowedPersonality,
                    VirtualSwitch, __VSwitchClusterAssignment,
                    __VSwitchPGAssignment,
                    BuildingPreference, MemberPriority, PriorityList],
    },
    'network': {
        'title': 'Network',
        'classes': [Network, NetworkEnvironment, RouterAddress, StaticRoute,
                    NetworkDevice, VlanInfo, ObservedMac, __ObservedVlan,
                    PortGroup, AddressAssignment, Interface, ServiceAddress,
                    NetworkCompartment],
    },
    'xtn': {
        'title': 'Transactions',
        'classes': [Xtn, XtnEnd, XtnDetail],
    },
    'branch': {
        'title': 'Configuration Branches',
        'classes': [Branch, Sandbox, Domain, Review],
    },
    'users': {
        'title': 'Users',
        'classes': [UserPrincipal, Realm, Role, User, NetGroupWhiteList],
    },
    'storage': {
        'title': 'Storage',
        'classes': [Disk, Share, Filesystem],
    },
}

###############################################################################

db = DbFactory()
Base.metadata.bind = db.engine
orm.configure_mappers()
Base.metadata.create_all()
Base.metadata.reflect()


def table_coverage_check():
    """
        Check that all of the tables that exist in the database have been
        included in model group.  This is to guard agains the model being
        updated and this piece of code not.
    """
    seen = {}
    for group in model_group:
        for cls in model_group[group]['classes']:
            tbl = cls.__tablename__
            seen[tbl] = 1
    for tbl in Base.metadata.tables:
        if tbl in seen:
            del seen[tbl]
        else:
            seen[tbl] = 0
    for tbl in seen:
        print "Table %s is missing from this script" % tbl


def write_schema_group_png(group):
    tables = list((Base.metadata.tables[cls.__tablename__]
                   for cls in model_group[group]['classes']))
    pngfile = os.path.join(opts.dir, "%s.%s.png" % (opts.prefix, group))
    schema2dot.create_schema_graph(tables=tables).write_png(pngfile)


def write_schema_html():
    htmlfile = os.path.join(opts.dir, "index.html")
    fh = open(htmlfile, 'w')
    fh.write("<html><head><title>AQDB Schema</title></head>")
    fh.write("<body><h1>AQDB Schema</h1>")
    for group in model_group:
        classes = model_group[group]['classes']
        title = model_group[group]['title']
        pngfile = "%s.%s.png" % (opts.prefix, group)
        fh.write("<hr/><h2>%s</h2>" % title)
        fh.write("""<img src="%s" alt="schema"/>""" % pngfile)
        fh.write("<table><tr><th>Class</th>\
            <th>Table</th><th>Documentation</th></tr>")
        for cls in classes:
            fh.write("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                     % (cls.__name__, cls.__tablename__, cls.__doc__))
        fh.write("</table>")
    fh.write("</body></html>")

table_coverage_check()

for group in model_group:
    write_schema_group_png(group)

write_schema_html()
