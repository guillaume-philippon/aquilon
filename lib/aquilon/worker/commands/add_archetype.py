# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2013,2014,2015,2016  Contributor
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

from sqlalchemy.inspection import inspect

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Archetype, Cluster
from aquilon.utils import validate_nlist_key
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.templates import Plenary


class CommandAddArchetype(BrokerCommand):

    required_parameters = ["archetype"]

    def render(self, session, archetype, cluster_type, compilable,
               description, comments, **_):
        validate_nlist_key('--archetype', archetype)

        def subclasses(cls):
            for subcls in cls.__subclasses__():
                for subsubcls in subclasses(subcls):
                    yield subsubcls
                yield subcls

        reserved_names = set(cls.prefix for cls in subclasses(Plenary))
        # There are also some top-level directories in the template repository
        reserved_names.update(["hardware", "pan", "t"])

        if archetype in reserved_names:
            raise ArgumentError("Archetype name %s is reserved." % archetype)

        Archetype.get_unique(session, archetype, preclude=True)

        if description is None:
            description = archetype
        if cluster_type:
            cls = Cluster.polymorphic_subclass(cluster_type,
                                               "Unknown cluster type")
            # Normalization
            cluster_type = inspect(cls).polymorphic_identity

        dbarch = Archetype(name=archetype, cluster_type=cluster_type,
                           outputdesc=description, comments=comments,
                           is_compileable=bool(compilable))

        session.add(dbarch)
        session.flush()

        return
