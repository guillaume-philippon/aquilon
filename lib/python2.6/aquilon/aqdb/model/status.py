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

from datetime import datetime

from sqlalchemy import (Column, Enum, Integer, DateTime, Sequence, 
                        String, ForeignKey, UniqueConstraint)

from aquilon.aqdb.model import Base
from aquilon.utils import monkeypatch
from aquilon.aqdb.column_types import Enum
from aquilon.exceptions_ import ArgumentError


''' 
This stateful view describes where the host is within it's
provisioning lifecycle. 
'''
_TN = 'status'
class Status(Base):
    transitions = {
               'blind'        : ['build', 'decommissioned'],
               'build'        : ['almostready','ready', 'decomissioned'],
               'install'      : ['build', 'decommissioned'],
               'almostready'  : ['ready', 'decommissioned'],
               'ready'        : ['rebuild', 'reinstall', 'failed', 
                                 'decommissioned'],
               'reinstall'    : ['rebuild', 'decommissioned'],
               'rebuild'      : ['ready', 'decommissioned'],
               'failed'       : ['rebuild', 'decommissioned'],
               'decommissioned' : [],
               }

    __tablename__ = _TN
    id = Column(Integer, Sequence('%s_id_seq'%(_TN)), primary_key=True)
    name = Column(Enum(32, transitions.keys()), nullable=False)
    creation_date = Column(DateTime, default=datetime.now, nullable=False)
    comments = Column(String(255), nullable=True)
    __mapper_args__ = { 'polymorphic_on': name }

    def __repr__(self):
        return str(self.name)

    def transition(self, session, obj, to):
        '''Transition to another state. 

        session -- the sqlalchemy session
        obj -- the object which wants to change state
        to -- the target state name

        returns a new state object for the target state, or
        throws an ArgumentError exception if the state cannot
        be reached. This method may be subclassed by states 
        if there is special logic regarding the transition.
        If the current state has an onLeave method, then the
        method will be called with the obj as an argument.
        If the target state has an onEnter method, then the
        method will be called with the obj as an argument.

        '''

        if to == self.name:
            return self

        if to not in Status.transitions:
            raise ArgumentError("status of %s is invalid" % to)

        targets = Status.transitions[self.name]
        if to not in targets:
            raise ArgumentError(("cannot change state to %s from %s. " +
                   "Legal states are: %s") % (to, self.name,
                   ", ".join(targets)))
        ret = Status.get_unique(session, to, compel=True)
        
        if hasattr(self, 'onLeave'):
            self.onLeave(obj)
        obj.status = ret
        session.add(obj)
        if hasattr(ret, 'onEnter'):
            ret = ret.onEnter(obj)
        return ret

hostlifecycle = Status.__table__
hostlifecycle.primary_key.name='%s_pk'%(_TN)
hostlifecycle.append_constraint(UniqueConstraint('name',name='%s_uk'%(_TN)))
hostlifecycle.info['unique_fields'] = ['name']

@monkeypatch(hostlifecycle)
def populate(sess, *args, **kw):
    from sqlalchemy.exceptions import IntegrityError

    statuslist = Status.transitions.keys()

    i = hostlifecycle.insert()
    for name in statuslist:
        try:
            i.execute(name=name)
        except IntegrityError:
            pass

    assert len(sess.query(Status).all()) == len(statuslist)


'''
The following classes are the actual lifecycle states for a host
'''

class Blind(Status):
    __mapper_args__ = {'polymorphic_identity': 'blind'}
    pass


class Decommissioned(Status):
    __mapper_args__ = {'polymorphic_identity': 'decommissioned'}
    pass


class Ready(Status):
    __mapper_args__ = {'polymorphic_identity': 'ready'}

    def onEnter(self, host):
        if host.cluster and host.cluster.status.name != 'ready':
            # logger.info("cluster is not ready, so forcing " +
            #             "state to almostready")
            return Almostready()
        return self


class Almostready(Status):
    __mapper_args__ = {'polymorphic_identity': 'almostready'}
    pass


class Install(Status):
    __mapper_args__ = {'polymorphic_identity': 'install'}
    pass


class Build(Status):
    __mapper_args__ = {'polymorphic_identity': 'build'}
    pass


class Rebuild(Status):
    __mapper_args__ = {'polymorphic_identity': 'rebuild'}
    pass


class Reinstall(Status):
    __mapper_args__ = {'polymorphic_identity': 'reinstall'}
    pass


class Failed(Status):
    __mapper_args__ = {'polymorphic_identity': 'failed'}
    pass

