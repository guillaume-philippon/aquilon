# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2008,2009,2010  Contributor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the EU DataGrid Software License.  You should
# have received a copy of the license with this program, and the
# license is published at
# http://eu-datagrid.web.cern.ch/eu-datagrid/license.html.
#
# THE FOLLOWING DISCLAIMER APPLIES TO ALL SOFTWARE CODE AND OTHER
# MATERIALS CONTRIBUTED IN CONNECTION WITH THIS PROGRAM.
#
# THIS SOFTWARE IS LICENSED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE AND ANY WARRANTY OF NON-INFRINGEMENT, ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. THIS
# SOFTWARE MAY BE REDISTRIBUTED TO OTHERS ONLY BY EFFECTIVELY USING
# THIS OR ANOTHER EQUIVALENT DISCLAIMER AS WELL AS ANY OTHER LICENSE
# TERMS THAT MAY APPLY.
"""Interface formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.server.formats.list import ListFormatter
from aquilon.aqdb.model import Interface


class InterfaceFormatter(ObjectFormatter):
    def format_raw(self, interface, indent=""):
        details = ''
        if interface.mac:
            details = [indent + "Interface: %s %s boot=%s" % (
                interface.name, interface.mac, interface.bootable)]
            obs = interface.last_observation
            if obs:
                details.append(indent + "  Last switch poll: %s port %s [%s]" %
                               (obs.switch.fqdn, obs.port_number,
                                obs.last_seen))
        else:
            details = [indent + "Interface: %s boot=%s (no mac addr)" % (
                interface.name, interface.bootable)]

        details.append(indent + "  Type: %s" % interface.interface_type)
        if interface.port_group:
            details.append(indent + "  Port Group: %s" % interface.port_group)

        hw = interface.hardware_entity
        hw_type = hw.hardware_type
        if hw_type == 'machine':
            details.append(indent + "  Attached to: machine %s" % hw.label)
        elif hw_type == 'switch':
            if hw.switch:
                details.append(indent + "  Attached to: switch %s" %
                                   ",".join([ts.fqdn for ts in hw.switch]))
            else:
                details.append("  Attached to: unnamed switch")
        elif hw_type == 'chassis':
            if hw.chassis_hw:
                details.append("  Attached to: chassis %s" %
                                   ",".join([c.fqdn for c in hw.chassis_hw]))
            else:
                details.append("  Attached to: unnamed chassis")
        if interface.system:
            details.append(indent + "  Provides: %s [%s]" %
                           (interface.system.fqdn, interface.system.ip))
        if interface.comments:
            details.append(indent + "  Comments: %s" % interface.comments)
        return "\n".join(details)

ObjectFormatter.handlers[Interface] = InterfaceFormatter()


class MissingManagersList(list):
    pass


class MissingManagersFormatter(ListFormatter):
    def format_raw(self, mmlist, indent=""):
        commands = []
        for interface in mmlist:
            host = interface.hardware_entity.host
            if host:
                # FIXME: Deal with multiple management interfaces?
                commands.append("aq add manager --hostname '%s' --ip 'IP'" %
                                host.fqdn)
            else:
                commands.append("# No host found for machine %s with management interface" %
                                interface.hardware_entity.label)
        return "\n".join(commands)

    def csv_fields(self, interface):
        host = interface.hardware_entity.host
        if host:
            return (host.fqdn,)
        else:
            return None

ObjectFormatter.handlers[MissingManagersList] = MissingManagersFormatter()
