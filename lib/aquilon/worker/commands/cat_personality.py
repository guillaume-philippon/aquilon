# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016  Contributor
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
"""Contains the logic for `aq cat --personality`."""

from aquilon.exceptions_ import ArgumentError, NotFoundException
from aquilon.aqdb.model import Personality
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.templates.personality import (PlenaryPersonalityParameter,
                                                  PlenaryPersonalityBase)


class CommandCatPersonality(BrokerCommand):

    required_parameters = ["personality"]

    # We do not lock the plenary while reading it
    _is_lock_free = True

    def render(self, generate, session, logger, personality,
               personality_stage, archetype, param_tmpl, **_):
        dbpersonality = Personality.get_unique(session, archetype=archetype,
                                               name=personality, compel=True)
        dbstage = dbpersonality.default_stage(personality_stage)

        if param_tmpl:
            try:
                param_def_holder = dbstage.archetype.param_def_holders[param_tmpl]
            except KeyError:
                raise ArgumentError("Unknown parameter template %s." % param_tmpl)

            try:
                dbparam = dbstage.parameters[param_def_holder]
            except KeyError:
                raise NotFoundException("No parameters found for template %s." %
                                        param_tmpl)

            plenary = PlenaryPersonalityParameter(dbparam, logger=logger)
        else:
            plenary = PlenaryPersonalityBase.get_plenary(dbstage,
                                                         logger=logger)

        if generate:
            return plenary._generate_content()
        else:
            return plenary.read()
