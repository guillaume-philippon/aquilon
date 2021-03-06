#
# Copyright (C) 2013,2014,2015  Contributor
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
%setup -n %{name}-%{unmangled_version}
grep -lrE '(import aquilon.*depends)|(from aquilon.*import depends)' . \
    |xargs sed -i '/\(import aquilon.*depends\)\|\(from aquilon.*import depends\)/d'
stylesheets=/usr/share/sgml/docbook/xsl-ns-stylesheets-$(rpm -q --qf %{VERSION} \
    docbook5-style-xsl)
sed -i '/ms.version/d' tools/gen_completion.py
sed -i "s:/ms/dist/fsf/PROJ/docbook-xsl-ns/.*/common:$stylesheets:" \
    doc/style-man.xsl
sed -i "s:/ms/dist/fsf/PROJ/docbook-xsl-ns/.*/common:$stylesheets:" \
    doc/style-html.xsl
sed -i '/# -- begin path_setup/,/# -- end path_setup/d' \
    bin/* sbin/*
