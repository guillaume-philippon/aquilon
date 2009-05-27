# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq map service`."""


from aquilon.exceptions_ import UnimplementedError
from aquilon.server.broker import BrokerCommand
from aquilon.aqdb.model import ServiceMap, PersonalityServiceMap
from aquilon.server.dbwrappers.service import get_service
from aquilon.server.dbwrappers.location import get_location
from aquilon.server.dbwrappers.personality import get_personality
from aquilon.server.dbwrappers.service_instance import get_service_instance


class CommandMapService(BrokerCommand):

    required_parameters = ["service", "instance", "archetype"]

    def render(self, session, service, instance, archetype, personality, **arguments):
        dbservice = get_service(session, service)
        dblocation = get_location(session, **arguments)
        dbinstance = get_service_instance(session, dbservice, instance)

        if archetype and personality:
            dbpersona = get_personality(session, archetype, personality)
            dbmap = session.query(PersonalityServiceMap)
            dbmap = dbmap.filter_by(personality=dbpersona).filter_by(
                location=dblocation, service_instance=dbinstance).first()
            if not dbmap:
                dbmap = PersonalityServiceMap(personality=dbpersona,
                                              service_instance=dbinstance,
                                              location=dblocation)
        elif archetype != 'aquilon':
            msg = "Archetype level ServiceMaps other than aquilon are not yet available"
            raise UnimplementedError(msg)

        else:
            dbmap = session.query(ServiceMap).filter_by(location=dblocation,
                service_instance=dbinstance).first()
            if not dbmap:
                dbmap = ServiceMap(service_instance=dbinstance, location=dblocation)

        session.add(dbmap)
        session.flush()
        session.refresh(dbservice)
        session.refresh(dbinstance)
        return
