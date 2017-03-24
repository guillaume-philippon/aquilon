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
"""Contains the logic for `aq update disk`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Machine, Disk, VirtualDisk, Filesystem, Share
from aquilon.utils import force_wwn
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.resources import find_resource


class CommandUpdateDisk(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["machine", "disk"]

    def render(self, session, plenaries, machine, disk, controller, share,
               filesystem, resourcegroup, address, comments, size, boot,
               snapshot, rename_to, wwn, bus_address, iops_limit, **_):
        dbmachine = Machine.get_unique(session, machine, compel=True)
        dbdisk = Disk.get_unique(session, device_name=disk, machine=dbmachine,
                                 compel=True)

        plenaries.add(dbmachine)

        if rename_to:
            Disk.get_unique(session, device_name=rename_to, machine=dbmachine,
                            preclude=True)
            dbdisk.device_name = rename_to

        if comments is not None:
            dbdisk.comments = comments

        if wwn is not None:
            wwn = force_wwn("--wwn", wwn)
            dbdisk.wwn = wwn

        if size is not None:
            dbdisk.capacity = size

        if controller:
            dbdisk.controller_type = controller

        if boot is not None:
            dbdisk.bootable = boot
            # There should be just one boot disk. We may need to re-think this
            # if we want to model software RAID in the database.
            for disk in dbmachine.disks:
                if disk == dbdisk:
                    continue
                if boot and disk.bootable:
                    disk.bootable = False

        if address is not None:
            dbdisk.address = address

        if bus_address is not None:
            dbdisk.bus_address = bus_address

        if snapshot is not None:
            if not isinstance(dbdisk, VirtualDisk):
                raise ArgumentError("Snapshot capability can only be set for "
                                    "virtual disks.")
            dbdisk.snapshotable = snapshot

        if iops_limit is not None:
            if not isinstance(dbdisk, VirtualDisk):
                raise ArgumentError("IOPS limit can only be set for virtual disks.")
            dbdisk.iops_limit = iops_limit

        if share or filesystem:
            if not isinstance(dbdisk, VirtualDisk):
                raise ArgumentError("Disk {0!s} of {1:l} is not a virtual "
                                    "disk, changing the backend store is not "
                                    "possible.".format(dbdisk, dbmachine))

            if share:
                dbres = find_resource(Share,
                                      dbmachine.vm_container.holder.holder_object,
                                      resourcegroup, share)
            elif filesystem:
                dbres = find_resource(Filesystem,
                                      dbmachine.vm_container.holder.holder_object,
                                      resourcegroup, filesystem)

            dbdisk.backing_store = dbres

        session.flush()

        plenaries.write()

        return
