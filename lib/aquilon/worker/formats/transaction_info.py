# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2011,2013,2014,2016  Contributor
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
""" Transaction formatter """

import calendar

from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import Xtn


class TransactionFormatter(ObjectFormatter):
    def fill_proto(self, xtn, skeleton, embedded=True, indirect_attrs=True):
        skeleton.start_time = calendar.timegm(xtn.start_time.utctimetuple())
        skeleton.username = xtn.username
        skeleton.command = xtn.command
        skeleton.return_code = xtn.return_code
        if xtn.end:
            skeleton.end_time = calendar.timegm(
                xtn.end.end_time.utctimetuple())
        else:
            # Need some sort of value for the protobuf (since protobufs do
            # not have a concept of null).
            skeleton.end_time = 0
        skeleton.is_readonly = int(xtn.is_readonly)

        for i in xtn.args:
            arg = skeleton.arguments.add()
            arg.name = i.name
            arg.value = i.value

ObjectFormatter.handlers[Xtn] = TransactionFormatter()
