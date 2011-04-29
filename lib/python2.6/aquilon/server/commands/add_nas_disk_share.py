# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2011  Contributor
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
"""Contains the logic for `aq add service`."""

from aquilon.exceptions_ import ArgumentError, NotFoundException, InternalError
from aquilon.server.broker import BrokerCommand
from aquilon.aqdb.model import Service, ServiceInstance
from aquilon.server.templates.base import PlenaryCollection
from aquilon.server.templates.service import (PlenaryService,
                                              PlenaryServiceInstance)


class CommandAddNASDiskShare(BrokerCommand):

    required_parameters = ["share"]

    def render(self, session, logger, share, comments, manager,
               **arguments):
        dbservice = Service.get_unique(session, name='nas_disk_share',
                                       compel=InternalError)
        plenaries = PlenaryCollection(logger=logger)
        plenaries.append(PlenaryService(dbservice, logger=logger))

        ServiceInstance.get_unique(session, service=dbservice,
                                   name=share, preclude=True)
        dbsi = ServiceInstance(service=dbservice, name=share,
                               comments=comments, manager=manager)
        session.add(dbsi)
        plenaries.append(PlenaryServiceInstance(dbservice, dbsi,
                                                logger=logger ))
        session.flush()
        plenaries.write()
        return