# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017  Contributor
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
"""Any work by the broker to write out (or read in?) templates lives here."""

import os
import logging
import time

from aquilon.config import Config, lookup_file_path
from aquilon.exceptions_ import ArgumentError, ProcessException, AquilonError
from aquilon.aqdb.model import (Host, Cluster, Fqdn, DnsDomain, DnsRecord,
                                HardwareEntity, Sandbox, Domain, Archetype,
                                Personality, PersonalityStage)
from aquilon.worker.logger import CLIENT_INFO
from aquilon.notify.index import trigger_notifications
from aquilon.worker.processes import run_command

LOGGER = logging.getLogger(__name__)


def template_branch_basedir(config, dbbranch, dbauthor=None):
    if isinstance(dbbranch, Sandbox):
        if not dbauthor:
            raise AquilonError("Missing required author to compile "
                               "{0:l}.".format(dbbranch))
        return os.path.join(config.get("broker", "templatesdir"),
                            dbauthor.name, dbbranch.name)
    else:
        return os.path.join(config.get("broker", "domainsdir"), dbbranch.name)


class TemplateDomain(object):

    def __init__(self, domain, author=None, logger=LOGGER):
        super(TemplateDomain, self).__init__()

        if isinstance(domain, Sandbox) and not author:
            raise AquilonError("No author information provided for {0:l}. If "
                               "the sandbox belonged to an user that got "
                               "deleted, then all hosts/clusters must be "
                               "moved to a sandbox owned by an existing user."
                               .format(domain))

        self.domain = domain
        self.author = author
        self.logger = logger

    def directories(self):
        """Return a list of directories required for compiling this domain"""
        config = Config()
        dirs = []

        if isinstance(self.domain, Domain):
            dirs.append(os.path.join(config.get("broker", "domainsdir"),
                                     self.domain.name))

        dirs.append(os.path.join(config.get("broker", "cfgdir"),
                                 "domains", self.domain.name))

        # This is a bit redundant. When creating the directories, the "clusters"
        # subdir would be enough; when removing them, the base dir would be
        # enough. Having both does not hurt and does not need such extra logic.
        dirs.append(os.path.join(config.get("broker", "quattordir"),
                                 "build", self.domain.name))
        dirs.append(os.path.join(config.get("broker", "quattordir"),
                                 "build", self.domain.name, "clusters"))

        return dirs

    def compile(self, session, only=None, panc_debug_include=None,
                panc_debug_exclude=None, cleandeps=False):
        """The build directories are checked and constructed
        if necessary, so no prior setup is required.

        The caller is responsible for locking.

        If the 'only' parameter is provided, then it should be a
        list or set containing the profiles that need to be compiled.

        May raise ArgumentError exception, else returns the standard
        output (as a string) of the compile
        """

        config = Config()

        templatedir = template_branch_basedir(config, self.domain, self.author)
        if not os.path.exists(templatedir):
            raise ArgumentError("Template directory '%s' does not exist." %
                                templatedir)

        self.logger.info("preparing domain %s for compile", self.domain.name)

        # Ensure that the compile directory is in a good state.
        outputdir = config.get("broker", "profilesdir")

        for d in self.directories() + [config.get("broker", "profilesdir")]:
            if not os.path.exists(d):
                try:
                    self.logger.info("creating %s", d)
                    os.makedirs(d)
                except OSError as e:
                    raise ArgumentError("Failed to mkdir %s: %s" % (d, e))

        nothing_to_do = True
        if only is not None:
            # "only" may be a generator, which may not yield any entries
            only = set(only)
            nothing_to_do = len(only) == 0
        else:
            hostnames = session.query(Fqdn.name.concat(".")
                                      .concat(DnsDomain.name).label('hostname'))
            hostnames = hostnames.select_from(Fqdn)
            hostnames = hostnames.join(DnsDomain)
            hostnames = hostnames.join(DnsRecord, HardwareEntity, Host)
            hostnames = hostnames.filter_by(branch=self.domain,
                                            sandbox_author=self.author)
            hostnames = hostnames.join(PersonalityStage, Personality, Archetype)
            hostnames = hostnames.filter_by(is_compileable=True)

            clusternames = session.query(Cluster.name)
            clusternames = clusternames.filter_by(branch=self.domain,
                                                  sandbox_author=self.author)
            clusternames = clusternames.join(PersonalityStage, Personality, Archetype)
            clusternames = clusternames.filter_by(is_compileable=True)

            if self.author:
                # Need to restrict to the subset of the sandbox managed
                # by this author.
                only = [row.hostname for row in hostnames]
                only.extend("clusters/%s" % c.name for c in clusternames)
                nothing_to_do = not bool(only)
            else:
                nothing_to_do = not hostnames.count() and not clusternames.count()

        if nothing_to_do:
            self.logger.client_info('No object profiles: nothing to do.')
            return

        panc_env = {"PATH": os.environ.get("PATH", "")}

        if config.has_option("tool_locations", "java_home"):
            java_home = config.get("tool_locations", "java_home")
            panc_env["PATH"] = "%s/bin:%s" % (java_home, panc_env["PATH"])
            panc_env["JAVA_HOME"] = java_home

        if config.has_option("tool_locations", "ant_home"):
            ant_home = config.get("tool_locations", "ant_home")
            panc_env["PATH"] = "%s/bin:%s" % (ant_home, panc_env["PATH"])
            # The ant wrapper is silly and it may pick up the wrong set of .jars
            # if ANT_HOME is not set
            panc_env["ANT_HOME"] = ant_home

        if config.has_option("broker", "ant_options"):
            panc_env["ANT_OPTS"] = config.get("broker", "ant_options")

        if config.getboolean('panc', 'gzip_output'):
            compress_suffix = ".gz"
        else:
            compress_suffix = ""

        if self.domain.formats:
            formats = [format + compress_suffix for format in
                       self.domain.formats.split(",")]
        else:
            formats = []
            if config.getboolean('panc', 'xml_profiles'):
                formats.append("pan" + compress_suffix)
            if config.getboolean('panc', 'json_profiles'):
                formats.append("json" + compress_suffix)

        suffixes = []
        if "pan" + compress_suffix in formats:
            suffixes.append(".xml" + compress_suffix)
        if "json" + compress_suffix in formats:
            suffixes.append(".json" + compress_suffix)

        formats.append("dep")

        if config.has_option("panc", "timeout"):
            args = ["timeout", config.get("panc", "timeout")]
            args.append(config.lookup_tool("ant"))
        else:
            args = ["ant"]

        args.append("--noconfig")
        args.append("-f")
        args.append(lookup_file_path("build.xml"))
        args.append("-Dbasedir=%s" % config.get("broker", "quattordir"))
        args.append("-Dpanc.jar=%s" % self.domain.compiler)
        args.append("-Dpanc.formats=%s" % ",".join(formats))
        args.append("-Dprofile.suffixes=%s" % ",".join(suffixes))
        args.append("-Dpanc.template_extension=%s" %
                    config.get("panc", "template_extension"))
        args.append("-Ddomain=%s" % self.domain.name)
        args.append("-Ddistributed.profiles=%s" % outputdir)
        args.append("-Dpanc.batch.size=%s" %
                    config.get("panc", "batch_size"))
        args.append("-Dant-contrib.jar=%s" %
                    config.get("tool_locations", "ant_contrib_jar"))
        if isinstance(self.domain, Sandbox):
            args.append("-Ddomain.templates=%s" % templatedir)
        if only:
            # Use -Dforce.build=true?
            # TODO: pass the list in a temp file
            args.append("-Dobject.profile=%s" % " ".join(only))
            args.append("compile.object.profile")
        else:
            # Technically this is the default, but being explicit
            # doesn't hurt.
            args.append("compile.domain.profiles")
        if panc_debug_include is not None:
            args.append("-Dpanc.debug.include=%s" % panc_debug_include)
        if panc_debug_exclude is not None:
            args.append("-Dpanc.debug.exclude=%s" % panc_debug_exclude)
        if cleandeps:
            # Cannot send a false value - the test in build.xml is for
            # whether or not the property is defined at all.
            args.append("-Dclean.dep.files=%s" % cleandeps)

        self.logger.info("starting compile")
        try:
            run_command(args, env=panc_env, logger=self.logger,
                        path=config.get("broker", "quattordir"),
                        stream_level=CLIENT_INFO)
        except ProcessException:
            raise ArgumentError("Compilation failed, see the compiler "
                                "messages for details.")

        # Ugly hack. The File.lastModified() method is supposed to have
        # millisecond granularity, but the actual implementation in Java 7
        # has 1 second granularity only. So if the compilation finishes in
        # less than a second, and something modifies the data within that
        # second, the panc dependency tracker will be unable to notice that
        # the object is out of date and needs to be recompiled. Sleeping a
        # bit works around the issue by making sure further modifications
        # to the source templates will have a different second value than
        # anything this compilation used.
        time.sleep(1)

        trigger_notifications(config, self.logger, CLIENT_INFO)
