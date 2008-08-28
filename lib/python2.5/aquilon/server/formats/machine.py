#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Machine formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.hw.machine import Machine


class MachineFormatter(ObjectFormatter):
    def format_raw(self, machine, indent=""):
        details = [indent + "%s: %s" %
                (machine.model.machine_type.capitalize(), machine.name)]
        if machine.host:
            details.append(indent + "  Allocated to host: %s"
                    % machine.host.fqdn)
        details.append(self.redirect_raw(machine.location, indent + "  "))
        details.append(self.redirect_raw(machine.model, indent + "  "))
        details.append(indent + "  Cpu: %s x %d" %
                (machine.cpu, machine.cpu_quantity))
        details.append(indent + "  Memory: %d MB" % machine.memory)
        if machine.serial_no:
            details.append(indent + "  Serial: %s" % machine.serial_no)
        for d in machine.disks:
            details.append(indent + "  Disk: %s %d GB %s"
                    % (d.device_name, d.capacity, d.disk_type.type))
        for p in machine.switchport:
            if p.interface:
                details.append(indent + "  Switch Port %d: %s %s %s" %
                        (p.port_number, p.interface.machine.model.machine_type,
                            p.interface.machine.name, p.interface.name))
            else:
                details.append(indent +
                        "  Switch Port %d: No interface recorded in aqdb" %
                        p.port_number)
        for i in machine.interfaces:
            details.append(indent + "  Interface: %s %s %s boot=%s" 
                    % (i.name, i.mac, i.ip, i.boot))
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


#if __name__=='__main__':