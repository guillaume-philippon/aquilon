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
"""Authorization stub for simple authorization checks."""

import re

from six.moves.configparser import RawConfigParser  # pylint: disable=F0401

from twisted.python import log

from aquilon.exceptions_ import AuthorizationException
from aquilon.config import Config, lookup_file_path

host_re = re.compile(r'^host/(.+)@([^@]+)$')


class AuthorizationBroker(object):
    """Handles any behind the scenes work in figuring out entitlements."""

    # Borg
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

        # TODO: Make the initialization more explicit
        if getattr(self, "config", None):
            return

        self.config = Config()

        self.action_whitelist = {}
        self.role_whitelist = {}
        self.default_allow = {}

        authz_config = lookup_file_path(self.config.get("broker",
                                                        "authorization_rules"))
        log.msg("Reading authorization rules from " + authz_config)
        rules = RawConfigParser()
        rules.read(authz_config)

        for section in rules.sections():
            if section.startswith("action-"):
                if not rules.has_option(section, "role_whitelist"):
                    continue
                action = section[7:]
                roles = set(s.strip() for s in
                            rules.get(section, "role_whitelist").split(","))
                self.action_whitelist[action] = roles
            elif section.startswith("role-"):
                role = section[5:]
                if rules.has_option(section, "allow_by_default") and \
                   rules.getboolean(section, "allow_by_default"):
                    self.default_allow[role] = True
                if not rules.has_option(section, "actions"):
                    continue
                actions = set(s.strip() for s in
                              rules.get(section, "actions").split(","))
                self.role_whitelist[role] = actions

    def raise_auth_error(self, principal, action, resource):
        auth_msg = self.config.get("broker", "authorization_error")
        raise AuthorizationException("Unauthorized access attempt by %s to %s "
                                     "on %s.  %s" %
                                     (principal, action, resource, auth_msg))

    # FIXME: Hard coded check for now.
    def check(self, principal, dbuser, action, resource):
        if action.startswith('show') or action.startswith('search') \
           or action.startswith('cat') or action == 'status' \
           or action == 'dump_dns':
            return True
        if dbuser is None:
            raise AuthorizationException("Unauthorized anonymous access "
                                         "attempt to %s on %s" %
                                         (action, resource))
        # Special-casing the aquilon hosts... this is a special user
        # that provides a bucket for all host-generated activity.
        if self._check_aquilonhost(principal, dbuser, resource):
            return True
        if dbuser.role.name == 'nobody':
            self.raise_auth_error(principal, action, resource)

        # First process the per-action whitelist
        if action in self.action_whitelist and \
           dbuser.role.name not in self.action_whitelist[action] and \
           dbuser.role.name != "aqd_admin":
            self.raise_auth_error(principal, action, resource)

        if dbuser.role.name in self.default_allow or \
           dbuser.role.name == "aqd_admin":
            return True

        if dbuser.role.name in self.role_whitelist and \
           action in self.role_whitelist[dbuser.role.name]:
            return True

        self.raise_auth_error(principal, action, resource)

    def _check_aquilonhost(self, principal, dbuser, resource):
        """ Return true if the incoming user is an aquilon host and this is
            one of the few things that a host is allowed to change on its
            own."""
        if dbuser.name != 'aquilonhost':
            return False
        m = host_re.match(principal)
        if not m:
            return False
        if resource.startswith("/host/%s/" % m.group(1)):
            return True
        return False

    def check_network_environment(self, dbuser, dbnet_env):
        """More hacky authorization code.

        This bit is a helper for restricting people from touching networks
        that are maintained in other systems.  That restriction can be
        overridden for a configured list of roles (like aqd_admin) for
        emergencies.

        Something saner should be done here when we have better entitlements.

        """
        if not dbnet_env.is_default:
            # rely on standard authorization for all other environments
            return
        default = self.config.get("site", "default_network_environment")
        conf_value = self.config.get("site", "change_default_netenv_roles")
        allowed_roles = conf_value.strip().split()
        if dbuser.role.name not in allowed_roles:
            raise AuthorizationException("Only users with %s can modify "
                                         "networks in the %s network "
                                         "environment." %
                                         (allowed_roles, default))
        return
