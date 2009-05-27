# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Machine formatter."""


from aquilon import const
from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import Machine


class MachineFormatter(ObjectFormatter):
    def format_raw(self, machine, indent=""):
        details = [indent + "%s: %s" %
                (machine.model.machine_type.capitalize(), machine.name)]
        if machine.host:
            details.append(indent + "  Allocated to host: %s [%s]"
                    % (machine.host.fqdn, machine.host.ip))
        for manager in machine.manager:
            details.append(indent + "  Manager: %s [%s]" % (manager.fqdn,
                                                            manager.ip))
        for dbauxiliary in machine.auxiliaries:
            details.append(indent + "  Auxiliary: %s [%s]" % (
                           dbauxiliary.fqdn, dbauxiliary.ip))
        # This is a bit of a hack.  Delegating out to the standard location
        # formatter now spews too much information about chassis.  Maybe
        # that will change when chassis has a corresponding hardware type.
        for location_type in const.location_types:
            if getattr(machine.location, location_type, None) is not None:
                details.append(indent + "  %s: %s" % (
                                    location_type.capitalize(),
                                    getattr(machine.location, location_type)))
                if location_type == 'rack':
                    details.append(indent + "    Row: %s" %
                                   machine.location.rack.rack_row)
                    details.append(indent + "    Column: %s" %
                                   machine.location.rack.rack_column)
        for slot in machine.chassis_slot:
            details.append(indent + "  Chassis: %s" % slot.chassis.fqdn)
            details.append(indent + "  Slot: %d" % slot.slot_number)
        details.append(self.redirect_raw(machine.model, indent + "  "))
        details.append(indent + "  Cpu: %s x %d" %
                (machine.cpu, machine.cpu_quantity))
        details.append(indent + "  Memory: %d MB" % machine.memory)
        if machine.serial_no:
            details.append(indent + "  Serial: %s" % machine.serial_no)
        for d in machine.disks:
            details.append(indent + "  Disk: %s %d GB %s"
                    % (d.device_name, d.capacity, d.disk_type.type))
        for i in machine.interfaces:
            details.append(self.redirect_raw(i, indent + "  "))
        if machine.comments:
            details.append(indent + "  Comments: %s" % machine.comments)
        return "\n".join(details)

    def get_header(self):
        """This is just an idea... not used anywhere (yet?)."""
        return "machine,rack,building,vendor,model,serial,interface,mac,ip"

    def format_csv(self, machine):
        """This was implemented specifically for tor_switch.  May need
        to check and do something different for other machine types.
        
        """
        results = []
        details = [machine.name, machine.location.rack,
                machine.location.building, machine.model.vendor.name,
                machine.model.name, machine.serial_no]
        if not machine.interfaces:
            details.extend([None, None, None])
            results.append(details)
        for i in machine.interfaces:
            full = details[:]
            full.extend([i.name, i.mac, i.ip])
            results.append(full)
        return "\n".join([",".join([str(detail or "") for detail in result])
            for result in results])

ObjectFormatter.handlers[Machine] = MachineFormatter()


class SimpleMachineList(list):
    pass

class SimpleMachineListFormatter(ObjectFormatter):
    def format_raw(self, smlist, indent=""):
        return str("\n".join([indent + machine.name for machine in smlist]))

ObjectFormatter.handlers[SimpleMachineList] = SimpleMachineListFormatter()


