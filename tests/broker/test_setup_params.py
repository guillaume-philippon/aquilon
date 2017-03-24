#!/usr/bin/env python
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2012,2013,2014,2015,2016  Contributor
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
"""Module for testing parameter support."""

import json

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from broker.brokertest import TestBrokerCommand

actions_schema = {
    "schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "definitions": {
        "dependency_list": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "uniqueItems": True,
        },
    },
    "patternProperties": {
        "^[a-zA-Z_][a-zA-Z0-9_.-]*$": {
            "type": "object",
            "properties": {
                "user": {
                    "type": "string",
                },
                "command": {
                    "type": "string",
                },
                "dir": {
                    "type": "string",
                    "pattern": "^/.*$",
                },
                "timeout": {
                    "type": "integer",
                    "minValue": 0,
                },
                "priority": {
                    "description": "Deprecated - has no effect",
                    "type": "integer",
                },
                "dependencies": {
                    "type": "object",
                    "properties": {
                        "pre": {
                            "$ref": "#/definitions/dependency_list",
                        },
                        "post": {
                            "$ref": "#/definitions/dependency_list",
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": ["user", "command"],
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

maint_window_schema = {
    "schema": "http://json-schema.org/draft-04/schema#",
    "type": "array",
    "uniqueItems": True,
    "items": {
        "additionalProperties": False,
        "type": "object",
        "properties": {
            "day": {
                "pattern": "^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$",
                "type": "string",
            },
            "start": {
                "pattern": "^[012][0-9]:[0-5][0-9]$",
                "type": "string",
            },
            "duration": {
                "type": "integer",
                "minValue": 1,
            },
            "breakfix": {
                "type": "boolean",
            },
        },
        "required": ["day", "start", "duration"],
    },
}

# validation parameters by templates
AQUILON_PARAM_DEFS = {
    "access": [
        {
            "path": "access/netgroup",
            "value_type": "list",
            "description": "netgroups access"
        },
        {
            "path": "access/users",
            "value_type": "list",
            "description": "users access"
        },
    ],
    "actions": [
        {
            "path": "actions",
            "value_type": "json",
            "schema": json.dumps(actions_schema)
        },
    ],
    "startup": [
        {
            "path": "startup/actions",
            "value_type": "list",
            "description": "startup actions"
        },
    ],
    "shutdown": [
        {
            "path": "shutdown/actions",
            "value_type": "list",
            "description": "shutdown actions"
        },
    ],
    "maintenance": [
        {
            "path": "maintenance/actions",
            "value_type": "list",
            "description": "maintenance actions"
        },
    ],
    "monitoring": [
        {
            "path": "monitoring/alert",
            "value_type": "json",
            "description": "monitoring alert"
        },
        {
            "path": "monitoring/metric",
            "value_type": "json",
            "description": "monitoring metric"
        },
    ],
    "espinfo": [
        {
            "path": "espinfo/function",
            "value_type": "string",
            "description": "espinfo function",
            "required": True
        },
        {
            "path": "espinfo/class",
            "value_type": "string",
            "description": "espinfo class",
            "required": True
        },
        {
            "path": "espinfo/users",
            "value_type": "list",
            "description": "espinfo users",
            "required": True
        },
        {
            "path": "espinfo/description",
            "value_type": "string",
            "description": "espinfo desc"
        },
    ],
    "windows": [
        {
            "path": "windows/windows",
            "value_type": "json",
            "required": True,
            "schema": json.dumps(maint_window_schema),
        }
    ],
}

ESX_CLUSTER_PARAM_DEFS = {
    "espinfo": [
        {
            "path": "espinfo/function",
            "value_type": "string",
            "description": "espinfo function",
            "required": True
        },
        {
            "path": "espinfo/class",
            "value_type": "string",
            "description": "espinfo class",
            "required": True
        },
    ],
    "windows": [
        {
            "path": "windows/windows",
            "value_type": "json",
            "required": True,
            "schema": json.dumps(maint_window_schema),
        }
    ],
}

HACLUSTER_PARAM_DEFS = {
    "espinfo": [
        {
            "path": "espinfo/class",
            "value_type": "string",
            "description": "espinfo class",
            "required": True
        },
        {
            "path": "espinfo/description",
            "value_type": "string",
            "description": "espinfo desc"
        },
    ],
}

VMHOST_PARAM_DEFS = {
    "espinfo": [
        {
            "path": "espinfo/function",
            "value_type": "string",
            "description": "espinfo function",
            "required": True
        },
        {
            "path": "espinfo/class",
            "value_type": "string",
            "description": "espinfo class",
            "required": True
        },
        {
            "path": "espinfo/users",
            "value_type": "list",
            "description": "espinfo users",
            "required": True
        },
    ],
    "windows": [
        {
            "path": "windows/windows",
            "value_type": "json",
            "required": True,
            "schema": json.dumps(maint_window_schema),
        }
    ],
}


class TestSetupParams(TestBrokerCommand):

    def add_param_def(self, archetype, template, params):
        cmd = ["add_parameter_definition", "--archetype", archetype,
               "--path", params["path"], "--template", template,
               "--value_type", params["value_type"]]
        if params.get("required", False):
            cmd.append("--required")
        if "activation" in params:
            cmd.extend(["--activation", params["activation"]])
        if "schema" in params:
            cmd.extend(["--schema", params["schema"]])

        self.noouttest(cmd)

    def test_100_add_parameter_definitions(self):
        for template, paramlist in AQUILON_PARAM_DEFS.items():
            for params in paramlist:
                self.add_param_def("aquilon", template, params)
        for template, paramlist in ESX_CLUSTER_PARAM_DEFS.items():
            for params in paramlist:
                self.add_param_def("esx_cluster", template, params)
        for template, paramlist in HACLUSTER_PARAM_DEFS.items():
            for params in paramlist:
                self.add_param_def("hacluster", template, params)
        for template, paramlist in VMHOST_PARAM_DEFS.items():
            for params in paramlist:
                self.add_param_def("vmhost", template, params)

    def test_110_search_by_template(self):
        command = ["search_parameter_definition", "--archetype", "aquilon",
                   "--template", "espinfo"]
        out = self.commandtest(command)
        self.matchoutput(out, "function", command)
        self.matchclean(out, "access", command)
        self.matchclean(out, "actions", command)
        self.matchclean(out, "windows", command)

    def test_110_search_by_template_bad(self):
        command = ["search_parameter_definition", "--archetype", "aquilon",
                   "--template", "does-not-exist"]
        self.noouttest(command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSetupParams)
    unittest.TextTestRunner(verbosity=2).run(suite)
