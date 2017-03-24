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
""" Helpers for managing DNS-related objects """

import socket

from sqlalchemy.orm import object_session, joinedload, lazyload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_

from aquilon.exceptions_ import ArgumentError, AquilonError, NotFoundException
from aquilon.aqdb.model import (Fqdn, DnsDomain, DnsRecord, ARecord,
                                DynamicStub, Alias, ReservedName, SrvRecord,
                                DnsEnvironment, AddressAssignment,
                                NetworkEnvironment, AddressAlias)
from aquilon.aqdb.model.dns_domain import parse_fqdn
from aquilon.aqdb.model.network import get_net_id_from_ip
from aquilon.worker.dbwrappers.interface import check_ip_restrictions


def delete_dns_record(dbdns_rec, locked=False, verify_assignments=False):
    """
    Delete a DNS record

    Deleting a DNS record is a bit tricky because we do not want to keep
    orphaned FQDN entries.

    Set locked=True if the involved DNS domain(s) and network are already locked
    by the caller.

    Set verify_assignments=True to forbid removing a DNS record which is still
    in use.
    """

    session = object_session(dbdns_rec)

    dbfqdn = dbdns_rec.fqdn
    targets = []
    if getattr(dbdns_rec, 'reverse_ptr', None):
        targets.append(dbdns_rec.reverse_ptr)
    if getattr(dbdns_rec, 'target', None):
        targets.append(dbdns_rec.target)

    # Lock order: DNS domain(s), network
    if not locked:
        dns_domains = [dbfqdn.dns_domain]
        for tgt in targets:
            if tgt.dns_domain in dns_domains:
                continue
            dns_domains.append(tgt.dns_domain)
        DnsDomain.lock_rows(dns_domains)

        if hasattr(dbdns_rec, 'network'):
            dbdns_rec.network.lock_row()

    if dbdns_rec.aliases:
        raise ArgumentError("{0} still has aliases, delete them "
                            "first.".format(dbdns_rec))
    if dbdns_rec.srv_records:
        raise ArgumentError("{0} is still in use by SRV records, delete them "
                            "first.".format(dbdns_rec))

    if dbdns_rec.address_aliases:
        raise ArgumentError("{0} still has address aliases, delete them "
                            "first.".format(dbdns_rec))

    # Do not allow deleting the DNS record if the IP address is still in
    # use - except if there are other DNS records having the same
    # address. Don't perform the test though if the caller is about to change
    # those assignments
    if verify_assignments and hasattr(dbdns_rec, 'assignments'):
        last_use = []
        for addr in dbdns_rec.assignments:
            if len(addr.dns_records) == 1:
                last_use.append(addr)
        if last_use:
            users = " ,".join(sorted(format(addr.interface, "l")
                                     for addr in last_use))
            raise ArgumentError("IP address %s is still in use by %s." %
                                (dbdns_rec.ip, users))

    # Delete the DNS record
    session.delete(dbdns_rec)
    session.flush()

    # Delete the FQDN if it is orphaned
    q = session.query(DnsRecord)
    q = q.filter_by(fqdn=dbfqdn)
    if q.count() == 0:
        session.delete(dbfqdn)
    else:
        session.expire(dbfqdn, ['dns_records'])

    # Delete the orphaned targets
    for tgt in targets:
        delete_target_if_needed(session, tgt)


def convert_reserved_to_arecord(session, dbdns_rec, dbnetwork, ip):
    comments = dbdns_rec.comments
    dbhw_ent = dbdns_rec.hardware_entity
    dbfqdn = dbdns_rec.fqdn

    with session.no_autoflush:
        session.delete(dbdns_rec)
        session.expire(dbfqdn, ['dns_records'])
        new_dnsrec = ARecord(fqdn=dbfqdn, ip=ip, network=dbnetwork,
                             comments=comments)
        session.add(new_dnsrec)
        if dbhw_ent:
            dbhw_ent.primary_name = new_dnsrec

    return new_dnsrec


def _check_netenv_compat(dbdns_rec, dbnet_env):
    """ Verify that a DNS record is consistent with a network environment """
    dbnetwork = dbdns_rec.network
    if dbnetwork.network_environment != dbnet_env:
        raise ArgumentError("Address {0:a} lives in {1:l}, not in {2:l}.  Use "
                            "the --network_environment option to select the "
                            "correct environment."
                            .format(dbdns_rec, dbnetwork.network_environment,
                                    dbnet_env))


def _forbid_dyndns(dbdns_rec):
    """ Raise an error if the address is reserved for dynamic DHCP """
    if isinstance(dbdns_rec, DynamicStub):
        raise ArgumentError("Address {0:a} is reserved for dynamic "
                            "DHCP.".format(dbdns_rec))


# Locking rules:
# - Locking the DNS domain ensures exclusive access to the name
# - Locking the network ensures exclusive access to the IP address allocation
def grab_address(session, fqdn, ip, network_environment=None,
                 dns_environment=None, comments=None,
                 allow_restricted_domain=False, allow_multi=False,
                 allow_reserved=False, allow_shared=False, relaxed=False,
                 preclude=False):
    """
    Take ownership of an address.

    This is a bit complicated because due to DNS propagation delays, we want to
    allow users to pre-define a DNS address and then assign the address to a
    host later.

    Parameters:
        session: SQLA session handle
        fqdn: the name to allocate/take over
        ip: the IP address to allocate/take over
        network_environment: where the IP address lives
        dns_enviromnent: where the FQDN lives
        comments: any comments to attach to the DNS record if it is created as new
        allow_restricted_domain: if True, adding entries to restricted DNS
            domains is allowed, otherwise it is denied. Default is False.
        allow_multi: if True, allow the same FQDN to be added multiple times with
            different IP addresses. Deault is False.
        allow_reserved: if True, allow creating a ReservedName instead of an
            ARecord if no IP address was specified. Default is False.
        allow_shared: if True, allow the same FQDN/IP to be used another time
            even if its already allocated.
        preclude: if True, forbid taking over an existing DNS record, even if it
            is not referenced by any AddressAssignment records. Default is
            False.
    """
    if not isinstance(network_environment, NetworkEnvironment):
        network_environment = NetworkEnvironment.get_unique_or_default(session,
                                                                       network_environment)
    if not dns_environment:
        dns_environment = network_environment.dns_environment
    elif not isinstance(dns_environment, DnsEnvironment):
        dns_environment = DnsEnvironment.get_unique(session, dns_environment,
                                                    compel=True)

    # Non-default DNS environments may contain anything, but we want to keep
    # the internal environment clean
    if dns_environment.is_default and not network_environment.is_default:
        raise ArgumentError("Entering external IP addresses to the "
                            "internal DNS environment is not allowed.")

    short, dbdns_domain = parse_fqdn(session, fqdn)

    # Lock the domain to prevent adding/deleting records while we're checking
    # FQDN etc. availability
    dbdns_domain.lock_row()

    if dbdns_domain.restricted and not allow_restricted_domain:
        raise ArgumentError("{0} is restricted, adding extra addresses "
                            "is not allowed.".format(dbdns_domain))

    dbfqdn = Fqdn.get_or_create(session, dns_environment=dns_environment,
                                name=short, dns_domain=dbdns_domain,
                                query_options=[joinedload('dns_records')])

    existing_record = None
    newly_created = False

    if ip:
        dbnetwork = get_net_id_from_ip(session, ip, network_environment)
        check_ip_restrictions(dbnetwork, ip, relaxed=relaxed)

        dbnetwork.lock_row()

        # No filtering on DNS environment. If an address is dynamic in one
        # environment, it should not be considered static in a different
        # environment.
        q = session.query(DynamicStub)
        q = q.filter_by(network=dbnetwork)
        q = q.filter_by(ip=ip)
        dbdns_rec = q.first()
        _forbid_dyndns(dbdns_rec)

        # Verify that no other record uses the same IP address, this time taking
        # the DNS environemt into consideration.
        # While the DNS would allow different A records to point to the same IP
        # address, the current user expectation is that creating a DNS entry
        # also counts as a reservation, so we can not allow this use case. If we
        # want to implement such a feature later, the best way would be to
        # subclass Alias and let that subclass emit an A record instead of a
        # CNAME when the dump_dns command is called.
        q = session.query(ARecord)
        q = q.filter_by(network=dbnetwork)
        q = q.filter_by(ip=ip)
        q = q.join(ARecord.fqdn)
        q = q.filter_by(dns_environment=dns_environment)
        dbrecords = q.all()
        if dbrecords and len(dbrecords) > 1:  # pragma: no cover
            # We're just trying to make sure this never happens
            raise AquilonError("IP address %s is referenced by multiple "
                               "DNS records: %s" %
                               (ip, ", ".join(sorted(format(rec, "a")
                                                     for rec in dbrecords))))
        if dbrecords and dbrecords[0].fqdn != dbfqdn:
            raise ArgumentError("IP address {0} is already in use by {1:l}."
                                .format(ip, dbrecords[0]))

        # Check if the name is used already
        for dbdns_rec in dbfqdn.dns_records:
            if isinstance(dbdns_rec, ARecord):
                _forbid_dyndns(dbdns_rec)
                _check_netenv_compat(dbdns_rec, network_environment)
                if dbdns_rec.ip == ip and dbdns_rec.network == dbnetwork:
                    existing_record = dbdns_rec
                elif not allow_multi:
                    raise ArgumentError("{0} points to a different IP address."
                                        .format(dbdns_rec))

            elif isinstance(dbdns_rec, ReservedName):
                existing_record = convert_reserved_to_arecord(session,
                                                              dbdns_rec,
                                                              dbnetwork, ip)
                newly_created = True
            else:
                # Exclude aliases etc.
                raise ArgumentError("{0} cannot be used for address assignment."
                                    .format(dbdns_rec))

        if not existing_record:
            existing_record = ARecord(fqdn=dbfqdn, ip=ip, network=dbnetwork,
                                      comments=comments)
            session.add(existing_record)
            newly_created = True
    else:
        if not dbfqdn.dns_records:
            # There's no IP, and the name did not exist before. Create a
            # reservation, but only if the caller allowed that use case.
            if not allow_reserved:
                raise ArgumentError("DNS Record %s does not exist." % dbfqdn)

            existing_record = ReservedName(fqdn=dbfqdn, comments=comments)
            newly_created = True
        else:
            # There's no IP, but the name is already in use. We need a single IP
            # address.
            if len(dbfqdn.dns_records) > 1:
                raise ArgumentError("{0} does not resolve to a single IP address."
                                    .format(dbfqdn))

            existing_record = dbfqdn.dns_records[0]
            _forbid_dyndns(existing_record)
            if not isinstance(existing_record, ARecord):
                # Exclude aliases etc.
                raise ArgumentError("{0} cannot be used for address assignment."
                                    .format(existing_record))

            # Verify that the existing record is in the network environment the
            # caller expects
            _check_netenv_compat(existing_record, network_environment)

            ip = existing_record.ip
            dbnetwork = existing_record.network

            dbnetwork.lock_row()

    if existing_record.hardware_entity:
        raise ArgumentError("{0} is already used as the primary name of {1:cl} "
                            "{1.label}.".format(existing_record,
                                                existing_record.hardware_entity))

    if preclude and not newly_created:
        raise ArgumentError("{0} already exists.".format(existing_record))

    if ip:
        q = session.query(AddressAssignment)
        q = q.with_polymorphic('*')
        q = q.filter_by(network=dbnetwork)
        q = q.filter_by(ip=ip)
        addr = q.first()
        if addr:
            if allow_shared:
                if not addr.is_shared:
                    raise ArgumentError("IP address {0} is not shared and "
                                        "already in use by {1:l}"
                                        ".".format(ip, addr.interface))
                # else: existing shared address, no problem
            else:
                raise ArgumentError("IP address {0} is already in use by "
                                    "{1:l}.".format(ip, addr.interface))
        # else: no existing address, no problem

        if existing_record.service_addresses and not allow_shared:
            raise ArgumentError("{0} is already being used as a service address."
                                .format(existing_record))

    return (existing_record, newly_created)


def update_address(session, dbdns_rec, ip, dbnetwork):
    if dbdns_rec.hardware_entity:
        raise ArgumentError("{0} is a primary name, and its IP address "
                            "cannot be changed.".format(dbdns_rec))

    if dbdns_rec.assignments:
        ifaces = ", ".join(sorted(addr.interface.qualified_name
                                  for addr in dbdns_rec.assignments))
        raise ArgumentError("{0} is already used by the following "
                            "interfaces, and its IP address cannot be "
                            "changed: {1!s}."
                            .format(dbdns_rec, ifaces))

    q = session.query(ARecord)
    q = q.filter_by(network=dbnetwork, ip=ip)
    q = q.join(ARecord.fqdn)
    q = q.filter_by(dns_environment=dbdns_rec.fqdn.dns_environment)
    existing = q.first()
    if existing:
        raise ArgumentError("IP address {0!s} is already used by "
                            "{1:l}." .format(ip, existing))

    dbdns_rec.network = dbnetwork
    dbdns_rec.ip = ip


def create_target_if_needed(session, logger, target, dbdns_env):
    """
    Create FQDNs in restricted domains.

    This is used to allow pointing CNAME and PTR records to DNS domains we
    otherwise don't manage.
    """
    name, dbtarget_domain = parse_fqdn(session, target)

    dbtarget_domain.lock_row()

    q = session.query(Fqdn)
    q = q.filter_by(dns_environment=dbdns_env)
    q = q.filter_by(dns_domain=dbtarget_domain)
    q = q.filter_by(name=name)
    try:
        dbtarget = q.one()
    except NoResultFound:
        if not dbtarget_domain.restricted:
            raise NotFoundException("Target FQDN {0} does not exist in {1:l}."
                                    .format(target, dbdns_env))

        dbtarget = Fqdn(name=name, dns_domain=dbtarget_domain,
                        dns_environment=dbdns_env)

        try:
            socket.gethostbyname(dbtarget.fqdn)
        except socket.gaierror as e:
            logger.warning("WARNING: Will create a reference to {0.fqdn!s}, "
                           "but trying to resolve it resulted in an error: "
                           "{1.strerror}.".format(dbtarget, e))

        session.add(dbtarget)
        dbtarget_rec = ReservedName(fqdn=dbtarget)
        session.add(dbtarget_rec)

    return dbtarget


def delete_target_if_needed(session, dbtarget):
    session.flush()

    # If there's a ReservedName pointing to this FQDN and we're in a restricted
    # domain, then auto-remove the ReservedName entry
    if dbtarget.dns_records:
        if not dbtarget.dns_domain.restricted:
            return

        for dbdns_rec in dbtarget.dns_records:
            if not isinstance(dbdns_rec, ReservedName):
                return
            if dbdns_rec.hardware_entity:
                return
    else:
        dbdns_rec = None

    # Check if the FQDN is still the target of an existing alias, service record
    # or reverse PTR record
    q = session.query(DnsRecord)
    q = q.with_polymorphic([ARecord, Alias, AddressAlias, SrvRecord])
    q = q.filter(or_(ARecord.reverse_ptr_id == dbtarget.id,
                     Alias.target_id == dbtarget.id,
                     AddressAlias.target_id == dbtarget.id,
                     SrvRecord.target_id == dbtarget.id))
    q = q.options(lazyload('fqdn'))
    if not q.count():
        for dbdns_rec in dbtarget.dns_records:
            session.delete(dbdns_rec)
        session.delete(dbtarget)
    else:
        session.expire(dbtarget, ['dns_records'])


def set_reverse_ptr(session, logger, dbdns_rec, reverse_ptr):
    if isinstance(reverse_ptr, Fqdn):
        dbreverse = reverse_ptr
    else:
        dbreverse = create_target_if_needed(session, logger, reverse_ptr,
                                            dbdns_rec.fqdn.dns_environment)
    # Technically the reverse PTR could point to other types, not just
    # the types listed below, but there are no use cases for that, so
    # better avoid confusion
    for rec in dbreverse.dns_records:
        if not isinstance(rec, (ARecord, AddressAlias, Alias, ReservedName)):
            raise ArgumentError("The reverse PTR cannot point "
                                "to {0:lc}.".format(rec))
    if dbreverse != dbdns_rec.fqdn:
        try:
            dbdns_rec.reverse_ptr = dbreverse
        except ValueError as err:
            raise ArgumentError(err)
    else:
        dbdns_rec.reverse_ptr = None
