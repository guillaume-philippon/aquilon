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
""" Representation of DNS A records """

from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.orm import (relation, backref, mapper, deferred, object_session,
                            validates)
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.sql import join, and_

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Network, NetworkEnvironment, DnsRecord, Fqdn
from aquilon.aqdb.column_types import IPV4

_TN = 'a_record'
_DTN = 'dynamic_stub'


class ARecord(DnsRecord):
    __tablename__ = _TN
    _class_label = 'DNS Record'

    dns_record_id = Column(ForeignKey(DnsRecord.id, ondelete='CASCADE'),
                           primary_key=True)

    ip = Column(IPV4, nullable=False)

    network_id = Column(ForeignKey(Network.id), nullable=False)

    reverse_ptr_id = Column(ForeignKey(Fqdn.id, name='%s_reverse_ptr_fk' % _TN,
                                       ondelete='SET NULL'),
                            nullable=True, index=True)

    network = relation(Network, innerjoin=True,
                       backref=backref('dns_records', passive_deletes=True))

    reverse_ptr = relation(Fqdn, foreign_keys=reverse_ptr_id,
                           backref=backref('reverse_entries',
                                           passive_deletes=True))

    __table_args__ = (Index("%s_network_ip_idx" % _TN, network_id, ip),
                      {'info': {'unique_fields': ['fqdn'],
                                'extra_search_fields': ['ip', 'network',
                                                        'dns_environment']}})
    __mapper_args__ = {'polymorphic_identity': _TN}

    @property
    def is_unused(self):
        if self.assignments:
            return False
        elif self.service_addresses:
            return False
        else:
            return True

    def __format__(self, format_spec):
        if format_spec != "a":
            return super(ARecord, self).__format__(format_spec)
        return "%s [%s]" % (self.fqdn, self.ip)

    def __init__(self, ip=None, network=None, fqdn=None, **kwargs):
        if not network:  # pragma: no cover
            raise ValueError("network argument is missing")
        if ip not in network.network:  # pragma: no cover
            raise ValueError("IP not inside network")

        if not fqdn:  # pragma: no cover
            raise ValueError("fqdn cannot be empty")

        # We can't share both the IP and the FQDN with an other A record. Only
        # do the query if the FQDN is already persistent
        if instance_state(fqdn).has_identity:
            session = object_session(fqdn)
            if not session:  # pragma: no cover
                raise ValueError("fqdn must be already part of a session")

            # Disable autoflush because self is not ready to be pushed to the DB
            # yet
            with session.no_autoflush:
                q = session.query(ARecord.id)
                q = q.filter_by(network=network)
                q = q.filter_by(ip=ip)
                q = q.filter_by(fqdn=fqdn)
                if q.all():  # pragma: no cover
                    raise ArgumentError("%s, ip %s already exists." %
                                        (self._get_class_label(), ip))

        super(ARecord, self).__init__(ip=ip, network=network, fqdn=fqdn,
                                      **kwargs)

    @validates('reverse_ptr')
    def _validate_reverse_ptr(self, key, value):
        return self.validate_reverse_ptr(key, value)

    def validate_reverse_ptr(self, key, value):  # pylint: disable=W0613
        if value and self.fqdn.dns_environment != value.dns_environment:  # pragma: no cover
            raise ValueError("DNS environment mismatch: %s != %s" %
                             (self.fqdn.dns_environment, value.dns_environment))
        return value

    def check_grn_conflict(self, grn):
        super(ARecord, self).check_grn_conflict(grn)
        if self.service_addresses:
            raise ArgumentError("{0} is a service address. GRN should not be set "
                                "but derived from the device.".format(self))

# Create a secondary mapper to allow filtering DNS entries based on the DNS
# environment associated with the network the address is allocated from:
#
#  +------------------+  (IP, network_id)  +--------+          +----+
#  |Address allocation|  ----------------  |A record|  ------  |FQDN|
#  +------------------+                    +--------+          +----+
#                                             |                  |
#                                (network_id) |                  | (dns_environment_id)
#                                             |                  |
#                                          +-------+           +-------------------+
#                                          |Network|  -------  |Network environment|
#                                          +-------+           +-------------------+
#
# So, we want to be able to create joins between an allocated address (IP and
# network_id pair embedded into an object) and an A record, but we don't want to
# mix different DNS views together, so the join needs to be restricted to a
# single DNS environment. The mapper below implements the right side of the
# above graph (everything except the address allocation object) with the
# required filtering.
__j = join(ARecord, Fqdn, ARecord.fqdn_id == Fqdn.id)
__j = __j.join(NetworkEnvironment,
               Fqdn.dns_environment_id == NetworkEnvironment.dns_environment_id)
__j = __j.join(Network, and_(Network.id == ARecord.network_id,
                             Network.network_environment_id == NetworkEnvironment.id))

dns_fqdn_mapper = mapper(ARecord, __j,
                         # Only map the columns from the join which ARecord
                         # would normally have
                         include_properties=(DnsRecord.__table__.c.values() +
                                             ARecord.__table__.c.values()),
                         properties={
                             # Both DnsRecord and Fqdn have a column named 'id'.
                             # Tell the ORM that DnsRecord.fqdn_id and Fqdn.id are
                             # really the same thing due to the join condition
                             'fqdn_id': [__j.c.fqdn_id, __j.c.dns_record_fqdn_id],

                             # Usually these columns are not needed, so don't
                             # load them automatically
                             'creation_date': deferred(__j.c.dns_record_creation_date),
                             'comments': deferred(__j.c.dns_record_comments),

                             # Make sure FQDNs are eager loaded when using this
                             # mapper. This will cause fqdn being joined twice,
                             # but there's no way to tell SQLAlchemy that this
                             # information is already present in __j.
                             'fqdn': relation(Fqdn, lazy=False, innerjoin=True,
                                              primaryjoin=__j.c.dns_record_fqdn_id == Fqdn.id)
                         },
                         polymorphic_identity=_TN,
                         primary_key=__j.c.a_record_dns_record_id,
                         non_primary=True)


class DynamicStub(ARecord):
    """
        DynamicStub is a hack to handle stand alone DNS records for dynamic
        hosts prior to having a properly reworked set of tables for DNS
        information. It should not be used by anything other than to create host
        records for virtual machines using names similar to
        'dynamic-1-2-3-4.subdomain.ms.com'
    """
    __tablename__ = _DTN
    __mapper_args__ = {'polymorphic_identity': _DTN}
    _class_label = 'Dynamic Stub'

    dns_record_id = Column(ForeignKey(ARecord.dns_record_id,
                                      ondelete='CASCADE'),
                           primary_key=True)

    __table_args__ = ({'info': {'unique_fields': ['fqdn'],
                                'extra_search_fields': ['ip', 'network',
                                                        'dns_environment']}},)

    def validate_reverse_ptr(self, key, value):
        super(DynamicStub, self).validate_reverse_ptr(key, value)
        if value:
            raise ValueError("The reverse PTR record cannot be set for "
                             "DNS records used for dynamic DHCP.")
        return value

Network.dynamic_stubs = relation(DynamicStub, order_by=[DynamicStub.ip],
                                 viewonly=True)
