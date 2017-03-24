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
"""Interface formatter."""

from operator import attrgetter

from aquilon.aqdb.model import (Interface, PublicInterface, ManagementInterface,
                                OnboardInterface, VlanInterface,
                                BondingInterface, BridgeInterface,
                                LoopbackInterface, VirtualInterface,
                                PhysicalInterface)
from aquilon.aqdb.model.feature import interface_features
from aquilon.worker.formats.formatters import ObjectFormatter


class InterfaceFormatter(ObjectFormatter):
    def format_raw(self, interface, indent="", embedded=True,
                   indirect_attrs=True):
        details = ''

        if interface.hardware_entity.host:
            dbstage = interface.hardware_entity.host.personality_stage
        else:
            dbstage = None

        flags = []
        if interface.bootable:
            flags.append("boot")
        if interface.default_route:
            flags.append("default_route")
        if flags:
            flagstr = " [" + ", ".join(flags) + "]"
        else:
            flagstr = ""

        if interface.mac:
            details = [indent + "Interface: %s %s%s" % (interface.name,
                                                        interface.mac, flagstr)]
            obs = interface.last_observation
            if obs:
                details.append(indent + "  Last switch poll: %s port %s [%s]" %
                               (obs.network_device, obs.port, obs.last_seen))
        else:
            details = [indent + "Interface: %s (no MAC addr)%s" %
                       (interface.name, flagstr)]

        details.append(indent + "  Type: %s" % interface.interface_type)
        if interface.model_allowed:
            details.append(indent + "  {0:c}: {0.name} {1:c}: {1.name}"
                           .format(interface.model.vendor, interface.model))
        if interface.bus_address:
            details.append(indent + "  Controller Bus Address: %s" %
                           interface.bus_address)
        if interface.port_group:
            details.append(indent + "  {0:c}: {0.name}"
                           .format(interface.port_group))
            details.append(indent + "    Network: %s" %
                           interface.port_group.network)
        elif interface.port_group_name:
            details.append(indent + "  Port Group: %s" % interface.port_group_name)

        if hasattr(interface, "vlan_id"):
            details.append(indent + "  Parent Interface: %s, VLAN ID: %s" %
                           (interface.parent.name, interface.vlan_id))

        if interface.master_id is not None:
            details.append(indent + "  Master Interface: %s" %
                           interface.master.name)

        if interface.assignments:
            details.append(indent + "  {0:c}: {0.name}"
                           .format(interface.assignments[0].network.network_environment))

        static_routes = set()
        for addr in interface.assignments:
            if addr.fqdns:
                names = ", ".join(sorted(str(fqdn) for fqdn in addr.fqdns))
            else:
                names = "unknown"

            tags = []
            if addr.label:
                tags.append("label: %s" % addr.label)
            if addr.is_shared:
                tags.append("shared")
                tags.append("priority: %s" % addr.priority)
            if tags:
                tagstr = " (%s)" % ", ".join(tags)
            else:
                tagstr = ""
            details.append(indent + "  Provides: %s [%s]%s" %
                           (names, addr.ip, tagstr))
            static_routes |= set(addr.network.personality_static_routes(dbstage))

            for dns_record in addr.dns_records:
                if dns_record.alias_cnt:
                    details.append(indent + "  Aliases: %s" %
                                   ", ".join(sorted(str(a.fqdn) for a in
                                                    dns_record.all_aliases)))

        for route in sorted(static_routes,
                            key=attrgetter('destination', 'gateway_ip')):
            details.append(indent + "  {0:c}: {0.destination} gateway {0.gateway_ip}"
                           .format(route))
            if route.personality_stage:
                details.append(indent + "    {0:c}: {0.name} {1:c}: {1.name}"
                               .format(route.personality_stage.personality,
                                       route.personality_stage.archetype))
            if route.comments:
                details.append(indent + "    Comments: %s" % route.comments)

        if dbstage:
            for feature in sorted(interface_features(dbstage, interface),
                                  key=attrgetter('name')):
                details.append(indent + "  Template: %s" % feature.cfg_path)

        if interface.comments:
            details.append(indent + "  Comments: %s" % interface.comments)
        return "\n".join(details)

    def fill_proto(self, interface, skeleton, embedded=True,
                   indirect_attrs=True):
        skeleton.bootable = interface.bootable

        if interface.mac:
            skeleton.mac = str(interface.mac)

        skeleton.interface_type = interface.interface_type

        if interface.bus_address:
            skeleton.bus_address = interface.bus_address

        if interface.port_group:
            skeleton.port_group_usage = interface.port_group.usage
            skeleton.port_group_tag = interface.port_group.network_tag
            skeleton.port_group_name = interface.port_group.name
        elif interface.port_group_name:
            skeleton.port_group_name = interface.port_group_name

        if interface.model_allowed and indirect_attrs:
            self.redirect_proto(interface.model, skeleton.model)

ObjectFormatter.handlers[Interface] = InterfaceFormatter()
ObjectFormatter.handlers[PublicInterface] = InterfaceFormatter()
ObjectFormatter.handlers[ManagementInterface] = InterfaceFormatter()
ObjectFormatter.handlers[OnboardInterface] = InterfaceFormatter()
ObjectFormatter.handlers[VlanInterface] = InterfaceFormatter()
ObjectFormatter.handlers[BondingInterface] = InterfaceFormatter()
ObjectFormatter.handlers[BridgeInterface] = InterfaceFormatter()
ObjectFormatter.handlers[LoopbackInterface] = InterfaceFormatter()
ObjectFormatter.handlers[VirtualInterface] = InterfaceFormatter()
ObjectFormatter.handlers[PhysicalInterface] = InterfaceFormatter()
