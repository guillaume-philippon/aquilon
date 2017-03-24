# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2012,2013,2014,2015,2016  Contributor
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
"""Contains the logic for `aq search dns `."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import (DnsRecord, ARecord, DynamicStub, Alias,
                                SrvRecord, Fqdn, AddressAlias, ReservedName,
                                DnsDomain, DnsEnvironment, Network,
                                AddressAssignment, ServiceAddress)
from aquilon.aqdb.model.network_environment import get_net_dns_env
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.formats.list import StringAttributeList

from sqlalchemy.orm import (contains_eager, undefer, subqueryload, lazyload,
                            aliased)
from sqlalchemy.sql import or_, and_, null

# Map standard DNS record types to our internal types
DNS_RRTYPE_MAP = {'a': ARecord,
                  'cname': Alias,
                  'srv': SrvRecord}

# Constants for figuring out which parameters are valid for which record types
_target_set = frozenset([Alias, SrvRecord, AddressAlias])
_ip_set = frozenset([ARecord, DynamicStub])
_primary_name_set = frozenset([ARecord, ReservedName])


def update_classes(current_set, allowed_set):
    """
    Small helper for filtering options.

    For the first option, we want the set of possible classes initialized; for
    any further options, we want the existing set to be restricted. If the set
    becomes empty, then we have conflicting options.
    """
    if not current_set:
        current_set |= allowed_set
    else:
        current_set &= allowed_set

    if not current_set:
        raise ArgumentError("Conflicting search criteria has been specified.")


class CommandSearchDns(BrokerCommand):

    required_parameters = []

    def render(self, session, fqdn, dns_environment, dns_domain, shortname,
               record_type, ip, network, network_environment, target,
               target_domain, target_environment, primary_name, used,
               reverse_override, reverse_ptr, fullinfo, style, **_):

        # Figure out if we can restrict the types of DNS records based on the
        # options
        subclasses = set()
        if ip or network or network_environment or used is not None or \
           reverse_override is not None or reverse_ptr:
            update_classes(subclasses, _ip_set)
        if primary_name is not None:
            update_classes(subclasses, _primary_name_set)
        if target or target_domain or target_environment:
            update_classes(subclasses, _target_set)

        # Figure out the base class of the query. If the options already
        # restrict the choice to a single subclass of DnsRecord, then we want to
        # query on that, to force an inner join to be used.
        if record_type:
            record_type = record_type.strip().lower()
            if record_type in DNS_RRTYPE_MAP:
                cls = DNS_RRTYPE_MAP[record_type]
            else:
                cls = DnsRecord.polymorphic_subclass(record_type,
                                                     "Unknown DNS record type")
            if subclasses and cls not in subclasses:
                raise ArgumentError("Conflicting search criteria has been specified.")
            q = session.query(cls)
        else:
            if len(subclasses) == 1:
                cls = subclasses.pop()
                q = session.query(cls)
            else:
                cls = DnsRecord
                q = session.query(cls)
                if subclasses:
                    q = q.with_polymorphic(subclasses)
                else:
                    q = q.with_polymorphic('*')

        dbnet_env, dbdns_env = get_net_dns_env(session, network_environment,
                                               dns_environment)

        if fqdn:
            dbfqdn = Fqdn.get_unique(session, fqdn=fqdn,
                                     dns_environment=dbdns_env, compel=True)
            q = q.filter_by(fqdn=dbfqdn)

        q = q.join((Fqdn, DnsRecord.fqdn_id == Fqdn.id))
        q = q.filter_by(dns_environment=dbdns_env)
        q = q.options(contains_eager('fqdn'))

        if dns_domain:
            dbdns_domain = DnsDomain.get_unique(session, dns_domain,
                                                compel=True)
            q = q.filter_by(dns_domain=dbdns_domain)
        if shortname:
            q = q.filter_by(name=shortname)

        q = q.join(DnsDomain)
        q = q.options(contains_eager('fqdn.dns_domain'))
        q = q.order_by(Fqdn.name, DnsDomain.name)

        if ip:
            q = q.filter(ARecord.ip == ip)
            q = q.join(Network, aliased=True)
            q = q.filter_by(network_environment=dbnet_env)
            q = q.reset_joinpoint()
        if network:
            dbnetwork = Network.get_unique(session, network,
                                           network_environment=dbnet_env, compel=True)
            q = q.filter(ARecord.network == dbnetwork)
        if target:
            if target_environment:
                dbtgt_env = DnsEnvironment.get_unique_or_default(session,
                                                                 target_environment)
            else:
                dbtgt_env = dbdns_env

            dbtarget = Fqdn.get_unique(session, fqdn=target,
                                       dns_environment=dbtgt_env, compel=True)
            if cls != DnsRecord:
                q = q.filter(cls.target == dbtarget)
            else:
                q = q.filter(or_(Alias.target == dbtarget,
                                 SrvRecord.target == dbtarget,
                                 AddressAlias.target == dbtarget))
        if target_domain:
            dbdns_domain = DnsDomain.get_unique(session, target_domain,
                                                compel=True)
            TargetFqdn = aliased(Fqdn)

            if cls != DnsRecord:
                q = q.join(TargetFqdn, cls.target)
            else:
                q = q.join((TargetFqdn, or_(Alias.target_id == TargetFqdn.id,
                                            SrvRecord.target_id == TargetFqdn.id,
                                            AddressAlias.target_id == TargetFqdn.id)))
            q = q.filter(TargetFqdn.dns_domain == dbdns_domain)
        if primary_name is not None:
            if primary_name:
                q = q.filter(DnsRecord.hardware_entity.has())
            else:
                q = q.filter(~DnsRecord.hardware_entity.has())
        if used is not None:
            AAlias = aliased(AddressAssignment)
            SAlias = aliased(ServiceAddress)
            q = q.outerjoin(AAlias,
                            and_(ARecord.network_id == AAlias.network_id,
                                 ARecord.ip == AAlias.ip))
            q = q.outerjoin(SAlias, ARecord.service_addresses)
            if used:
                q = q.filter(or_(AAlias.id != null(),
                                 SAlias.id != null()))
            else:
                q = q.filter(and_(AAlias.id == null(),
                                  SAlias.id == null()))
            q = q.reset_joinpoint()
        if reverse_override is not None:
            if reverse_override:
                q = q.filter(ARecord.reverse_ptr.has())
            else:
                q = q.filter(~ARecord.reverse_ptr.has())
        if reverse_ptr:
            dbtarget = Fqdn.get_unique(session, fqdn=reverse_ptr,
                                       dns_environment=dbdns_env, compel=True)
            q = q.filter(ARecord.reverse_ptr == dbtarget)

        if fullinfo or style != "raw":
            q = q.options(undefer('comments'),
                          subqueryload('hardware_entity'),
                          lazyload('hardware_entity.primary_name'),
                          undefer('alias_cnt'),
                          undefer('address_alias_cnt'))
            return q.all()
        else:
            return StringAttributeList(q.all(), 'fqdn')
