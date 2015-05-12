# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2014  Contributor
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

from aquilon.worker.formats.formatters import ObjectFormatter


class CompileableFormatter(ObjectFormatter):
    def fill_proto(self, object, skeleton, embedded=True, indirect_attrs=True):
        skeleton.status = str(object.status)
        self.redirect_proto(object.personality_stage, skeleton.personality)
        self.redirect_proto(object.branch, skeleton.domain)
        if object.sandbox_author:
            skeleton.sandbox_author = str(object.sandbox_author)
