#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
""" Status is an overloaded term, but we use it to represent various stages of
    deployment, such as production, QA, dev, etc. each of which are also
    overloaded terms... """


import sys
import os

if __name__ == '__main__':
    DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.realpath(os.path.join(DIR, '..', '..', '..')))
    import aquilon.aqdb.depends

from aquilon.aqdb.db_factory import monkeypatch
from aquilon.aqdb.table_types.name_table import make_name_class


Status = make_name_class('Status','status')
status = Status.__table__

@monkeypatch(Status)
def __init__(self,name):
    e = "Status is a static table and can't be instanced, only queried."
    raise ValueError(e)

@monkeypatch(Status)
def __repr__(self):
    return str(self.name)

def populate(*args, **kw):
    from aquilon.aqdb.db_factory import db_factory, Base
    from sqlalchemy import insert

    dbf = db_factory()
    Base.metadata.bind = dbf.engine
    if 'debug' in args:
        Base.metadata.bind.echo = True
    s = dbf.session()

    status.create(checkfirst = True)

    if len(s.query(Status).all()) < 4:
        i=status.insert()
        for name in ['production','development','qa','build']:
            i.execute(name=name)
        #can't do the usual since we made __init__ raise an Exception
        #    j = Status(name = i)
        #    s.add(j)
        #s.commit()

    i = s.query(Status).all()
    assert len(i) == 4

    print 'created %s Statuses'%(len(i))

    if Base.metadata.bind.echo == True:
        Base.metadata.bind.echo == False
