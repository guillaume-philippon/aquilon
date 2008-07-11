#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""The tables/objects/mappings related to hardware in Aquilon. """
from datetime import datetime
import sys
import os

DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(DIR, '..'))
import depends

from sqlalchemy import (UniqueConstraint, Table, Column, Integer, DateTime,
                        Sequence, String, select, ForeignKey, Index)

from sqlalchemy.orm      import relation, deferred, backref

from column_types.aqstr  import AqStr
from db_factory          import Base
from cpu                 import Cpu
from model               import Model
from cfg.cfg_path        import CfgPath
from loc.location        import Location

#TODO: use selection of the machine specs to dynamically populate default
#     values for all of the attrs where its possible

class Machine(Base):
    __tablename__ = 'machine'
    id = Column(Integer, Sequence('machine_id_seq'), primary_key=True)

    name = Column('name', AqStr(32), nullable = False)

    location_id = Column(Integer, ForeignKey(
        'location.id', name ='machine_loc_fk'), nullable = False)

    model_id = Column(Integer, ForeignKey(
        'model.id', name = 'machine_model_fk'), nullable = False)

    cpu_id = Column(Integer, ForeignKey(
        'cpu.id', name = 'machine_cpu_fk'), nullable = False)

    cpu_quantity = Column(Integer, nullable = False, default = 2) #constrain?

    memory = Column(Integer, nullable = False, default = 512) #TODO: default?

    serial_no = Column(String(64), nullable = True)

    creation_date = deferred(Column(DateTime, default = datetime.now))
    comments = deferred(Column(String(255), nullable = True))

    location = relation(Location, uselist = False)
    model    = relation(Model, uselist = False)
    cpu      = relation(Cpu, uselist = False)

machine = Machine.__table__

machine.primary_key.name = 'machine_pk'

machine.append_constraint(
    UniqueConstraint('name',name = 'machine_name_uk')
)

#not needed for oracle due to UK
#Index('machine_name_ix', machine.c.name)
Index('machine_loc_ix',  machine.c.location_id)

def populate():
    from db_factory import db_factory, Base
    dbf = db_factory()
    Base.metadata.bind = dbf.engine
    Base.metadata.bind.echo = True
    s = dbf.session()

    machine.create(checkfirst = True)
#TODO:
#   check if it exists in dbdb minfo, and get from there if it does
#   and/or -dsdb option, and, make machine --like [other machine] + overrides