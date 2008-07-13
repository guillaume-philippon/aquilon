#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
""" If you can read this you should be documenting """


from __future__ import with_statement
from datetime import datetime
import sys
import os

if __name__ == '__main__':
    DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.realpath(os.path.join(DIR, '..', '..', '..')))
    import aquilon.aqdb.depends

from sqlalchemy import (Table, Column, Integer, DateTime, Sequence, String,
                        select, ForeignKey, PassiveDefault, UniqueConstraint)
from sqlalchemy.orm import mapper, relation, deferred

from aquilon.aqdb.column_types.aqstr import AqStr
from aquilon.aqdb.db_factory import Base
from aquilon.aqdb.hw.vendor import Vendor


class Cpu(Base):
    __tablename__ = 'cpu'
    id            = Column(Integer, Sequence('cpu_seq'), primary_key = True)
    name          = Column(AqStr(64), nullable = False)
    vendor_id     = Column(Integer, ForeignKey('vendor.id'), nullable = False)
    speed         = Column(Integer, nullable = False)
    creation_date = deferred(Column(DateTime, default = datetime.now))
    comments      = deferred(Column(String(255), nullable = True))
    vendor        = relation(Vendor)

cpu = Cpu.__table__
cpu.primary_key.name = 'cpu_pk'

cpu.append_constraint(
    UniqueConstraint('vendor_id','name','speed', name='cpu_nm_speed_uk'))

def populate(*args, **kw):
    from aquilon.aqdb.db_factory import db_factory, Base
    dbf = db_factory()
    Base.metadata.bind = dbf.engine
    if 'debug' in args:
        Base.metadata.bind.echo = True
    s = dbf.session()


    cpu.create(checkfirst = True)

    if len(s.query(Cpu).all()) < 1:
        import re
        m=re.compile('speed')
        cfg_base = dbf.config.get("broker", "kingdir")
        #get all dir names immediately under template-king/hardware/cpu/
        base=os.path.join(str(cfg_base),'hardware/cpu')
        cpus=[]

        for i in os.listdir(base):
            for j in os.listdir(os.path.join(base,i)):
                name = j.rstrip('.tpl').strip()
                with open(os.path.join(base,i,j),'r') as f:
                    assert(m)
                    for line in f.readlines():
                        a_match=m.search(line)
                        if a_match:
                            l,e,freq=line.partition('=')
                            assert(isinstance(freq,str))
                            speed=re.sub('\*MHz','',freq.strip().rstrip(';'))
                            #TODO: better checking if freq is ok here
                            if speed.isdigit():
                                cpus.append([i,name,speed])
                                break
                            else:
                                Assert(False)
                    f.close()

        for vendor,name,speed in cpus:
            kw={}
            vendor=s.query(Vendor).filter_by(name=vendor).first()
            assert(vendor)
            assert(name)
            assert(speed)
            if vendor:
                kw['vendor'] = vendor
                kw['name']   = name
                kw['speed']  = int(speed)
                a=Cpu(**kw)
                assert(isinstance(a,Cpu))
                try:
                    s.add(a)
                except Exception,e:
                    Session.rollback()
                    print e
                    continue
            else:
                msg="CREATE CPU: cant find vendor '%s'"%(vendor)
                if logging:
                    logging.error(msg)
                else:
                    print >> sys.stderr, msg
        try:
            s.commit()
        except Exception,e:
            s.rollback()
            sys.stderr.write(str(e))
        print 'Created cpus'

    if Base.metadata.bind.echo == True:
        Base.metadata.bind.echo == False
