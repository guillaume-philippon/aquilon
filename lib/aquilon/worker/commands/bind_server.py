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
"""Contains the logic for `aq bind server`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import (ServiceInstance, ServiceInstanceServer,
                                DnsEnvironment, Cluster, ServiceAddress, Alias)
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.change_management import validate_prod_service_instance
from aquilon.worker.dbwrappers.host import hostname_to_host
from aquilon.worker.dbwrappers.resources import get_resource_holder


def lookup_target(session, logger, plenaries, hostname, ip, cluster,
                  resourcegroup, service_address, alias):
    """
    Check the parameters of the server providing a given service

    Look for potential conflicts, and return a dict that is suitable to be
    passed to either the constructor of ServiceInstanceServer, or to the
    find_server() function.
    """

    params = {}

    if cluster and hostname:
        raise ArgumentError("Only one of --cluster and --hostname may be "
                            "specified.")

    if alias:
        dbdns_env = DnsEnvironment.get_unique_or_default(session)
        dbdns_rec = Alias.get_unique(session, fqdn=alias,
                                     dns_environment=dbdns_env, compel=True)
        params["alias"] = dbdns_rec

    if hostname:
        params["host"] = hostname_to_host(session, hostname)
        plenaries.add(params["host"])
    if cluster:
        params["cluster"] = Cluster.get_unique(session, cluster, compel=True)
        plenaries.add(params["cluster"])

    if service_address:
        # TODO: calling get_resource_holder() means doing redundant DB lookups
        # TODO: it would be nice to also accept an FQDN for the service address,
        # to be consistent with the usage of the --service_address option in
        # add_service_address/del_service_address
        holder = get_resource_holder(session, logger, hostname=hostname,
                                     cluster=cluster,
                                     resgroup=resourcegroup, compel=True)

        dbsrv_addr = ServiceAddress.get_unique(session,
                                               name=service_address,
                                               holder=holder, compel=True)
        params["service_address"] = dbsrv_addr
    elif ip:
        # --ip is only allowed for selecting an auxiliary IP of a host
        if "host" not in params:
            raise ArgumentError("The --ip option requires --host.")

        for addr in params["host"].hardware_entity.all_addresses():
            if ip == addr.ip:
                params["address_assignment"] = addr
                break
        else:
            raise ArgumentError("IP address {0!s} is not bound to {1:l}."
                                .format(ip, params["host"]))

    return params


def find_server(dbinstance, params):
    """
    Find an existing service binding matching the given parameters.
    """

    lookup_params = params.copy()

    for srv in dbinstance.servers:
        # Populating srv_params must be in sync with what lookup_target()
        # returns
        srv_params = {}
        for attr in ("host", "cluster", "service_address",
                     "address_assignment", "alias"):
            value = getattr(srv, attr, None)
            if value:
                srv_params[attr] = value

        if lookup_params == srv_params:
            return srv

    return None


class CommandBindServer(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["service", "instance"]

    def render(self, session, logger, plenaries, service, instance, position, hostname,
               cluster, ip, resourcegroup, service_address, alias,
               justification, reason, user, **_):
        # Check for invalid combinations. We allow binding as a server:
        # - a host, in which case the primary IP address will be used
        # - an auxiliary IP address of a host
        # - a service address of a host
        # - a service address of a cluster
        if ip:
            if cluster or not hostname:
                raise ArgumentError("Using the --ip option requires --hostname"
                                    "to be specified.")
        if cluster and not service_address:
            raise ArgumentError("Binding a cluster requires --service_address "
                                "to be specified.")

        dbinstance = ServiceInstance.get_unique(session, service=service,
                                                name=instance, compel=True)

        validate_prod_service_instance(dbinstance, user, justification, reason, logger)

        plenaries.add(dbinstance)

        if alias and not dbinstance.service.allow_alias_bindings:
            raise ArgumentError("Service %s is not configured to allow alias "
                                "bindings." % dbinstance.service)

        params = lookup_target(session, logger, plenaries, hostname, ip,
                               cluster, resourcegroup, service_address, alias)

        # TODO: someday we should verify that the target really points to the
        # host/cluster specified by the other options
        if "alias" in params and ("host" in params or "cluster" in params):
            logger.client_info("Warning: when using --alias, it is your "
                               "responsibility to ensure it really points to "
                               "the host/cluster you've specified - the broker "
                               "does not verify that.")

        with session.no_autoflush:
            dbsrv = find_server(dbinstance, params)
            if dbsrv:
                raise ArgumentError("The server binding already exists.")

            dbsrv = ServiceInstanceServer(**params)

            # The ordering_list will manage the position for us
            if position is not None:
                dbinstance.servers.insert(position, dbsrv)
            else:
                dbinstance.servers.append(dbsrv)

            if dbsrv.host:
                session.expire(dbsrv.host, ['services_provided'])
            if dbsrv.cluster:
                session.expire(dbsrv.cluster, ['services_provided'])

        session.flush()

        plenaries.write()

        return
