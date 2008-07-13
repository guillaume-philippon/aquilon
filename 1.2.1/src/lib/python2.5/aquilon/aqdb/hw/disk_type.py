#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
""" The high level configuration elements in use """


from datetime import datetime
import sys
import os

if __name__ == '__main__':
    DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.realpath(os.path.join(DIR, '..', '..', '..')))
    import aquilon.aqdb.depends

from aquilon.aqdb.table_types.subtype import subtype


DiskType = subtype('DiskType','disk_type','Disk Type: scsi, ccis, sata, etc.')
disk_type = DiskType.__table__
disk_type.primary_key.name = 'disk_type_pk'

_disk_types = ['ccis', 'ide', 'sas', 'sata', 'scsi', 'flash']

def populate(*args, **kw):
    from aquilon.aqdb.db_factory import db_factory, Base
    dbf = db_factory()
    Base.metadata.bind = dbf.engine
    if 'debug' in args:
        Base.metadata.bind.echo = True
    s = dbf.session()

    disk_type.create(checkfirst = True)

    if len(s.query(DiskType).all()) < 1:
        for t in _disk_types:
            dt = DiskType(type = t, comments = 'AutoPopulated')
            s.add(dt)
        s.commit()
    dt = s.query(DiskType).first()
    assert(dt)

    if Base.metadata.bind.echo == True:
        Base.metadata.bind.echo == False
