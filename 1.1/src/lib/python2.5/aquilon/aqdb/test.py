#!/ms/dist/python/PROJ/core/2.5.0/bin/python -W ignore
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent- tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
'''If you can read this, you should be Documenting'''

from sys import path

path.append('../..')

from aquilon.aqdb.utils.debug import ipshell
from db import meta, engine, Session


from location import *
from network import *
from service import *
from configuration import *
from hardware import *
from interfaces import *

s=Session()

c=s.query(Chassis).first()

m=Session.query(Machine).first()
p=m.location.parents()
w=p[0]

print 'm.interfaces: \n%s\n'%(m.interfaces)
print 'm.interfaces[0]: \n%s\n'%(m.interfaces[0])
print 'm.interfaces[0].__dict__: \n%s\n'%(m.interfaces[0].__dict__)
print 'm.interfaces[0].nic: \n%s\n'%(m.interfaces[0].nic)     
print 'm.interfaces[0].nic.driver: \n%s\n'%(m.interfaces[0].nic.driver)
print 'm.interfaces[0].nic.__dict__: \n%s\n'%(m.interfaces[0].nic.__dict__)


ipshell()
