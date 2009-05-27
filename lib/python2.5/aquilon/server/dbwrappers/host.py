# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Wrappers to make getting and using hosts simpler."""


from sqlalchemy.exceptions import InvalidRequestError

from aquilon.exceptions_ import ArgumentError, NotFoundException
from aquilon.aqdb.model import Host, DnsDomain
from aquilon.server.dbwrappers.system import get_system


def hostname_to_host(session, hostname):
    return get_system(session, hostname, Host, 'Host')

def get_host_build_item(self, dbhost, dbservice):
    for template in dbhost.templates:
        si = template.cfg_path.svc_inst
        if si and si.service == dbservice:
            return template
    return None

def get_host_dependencies(session, dbhost):
    """ returns a list of strings describing how a host is being used.
    If the host has no dependencies, then an empty list is returned
    """
    ret = []
    # XXX: Show any service instance which has dbhost as an element in host_list.hosts
    return ret
