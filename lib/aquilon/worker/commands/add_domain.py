# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2016  Contributor
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
"""Contains the logic for `aq add domain`."""

import os.path

from aquilon.exceptions_ import ArgumentError, InternalError, ProcessException
from aquilon.aqdb.model import Domain, Branch
from aquilon.utils import remove_dir
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.branch import add_branch
from aquilon.worker.processes import run_git, GitRepo


class CommandAddDomain(BrokerCommand):

    required_parameters = ["domain"]

    def render(self, session, logger, domain, track, start, change_manager,
               comments, allow_manage, **_):
        if track:
            dbtracked = Branch.get_unique(session, track, compel=True)
            if getattr(dbtracked, "tracked_branch", None):
                raise ArgumentError("Cannot nest tracking.  Try tracking "
                                    "{0:l} directly.".format(dbtracked.tracked_branch))
            dbstart = dbtracked
            if change_manager:
                raise ArgumentError("Cannot enforce a change manager for "
                                    "tracking domains.")
        else:
            dbtracked = None
            if not start:
                start = self.config.get("broker", "default_domain_start")
            dbstart = Branch.get_unique(session, start, compel=True)

        dbdomain = add_branch(session, self.config, Domain, domain,
                              tracked_branch=dbtracked,
                              requires_change_manager=bool(change_manager),
                              comments=comments, allow_manage=allow_manage)

        session.flush()

        domainsdir = self.config.get("broker", "domainsdir")
        clonedir = os.path.join(domainsdir, dbdomain.name)
        if os.path.exists(clonedir):
            raise InternalError("Domain directory already exists")

        kingdir = self.config.get("broker", "kingdir")
        cmd = ["branch"]
        if track:
            cmd.append("--track")
        else:
            cmd.append("--no-track")
        cmd.append(dbdomain.name)
        cmd.append(dbstart.name)

        kingrepo = GitRepo.template_king(logger)
        kingrepo.run(cmd)

        # If the branch command above fails the DB will roll back as normal.
        # If the command below fails we need to clean up from itself and above.
        try:
            run_git(["clone", "--branch", dbdomain.name, "--",
                     kingdir, dbdomain.name],
                    path=domainsdir, logger=logger)
        except ProcessException as e:  # pragma: no cover
            try:
                remove_dir(clonedir, logger=logger)
                kingrepo.run(["branch", "-D", dbdomain.name])
            except ProcessException as e2:
                logger.info("Exception while cleaning up: %s", e2)
            raise e
        return
