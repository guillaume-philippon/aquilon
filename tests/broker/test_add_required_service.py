#!/usr/bin/env python
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
"""Module for testing the add required service command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand

archetype_required = {
    'aquilon': ["dns", "aqd", "ntp", "bootserver", "support-group", "lemon",
                "syslogng"],
    'esx_cluster': ["esx_management_server"],
    'vmhost': ["dns", "ntp", "syslogng"],
}


class TestAddRequiredService(TestBrokerCommand):

    def test_100_add_afs(self):
        command = "add required service --service afs --archetype aquilon"
        command += " --justification tcm=12345678"
        self.noouttest(command.split(" "))

    def test_101_add_afs_redundant(self):
        command = ["add_required_service", "--service", "afs",
                   "--archetype", "aquilon", "--personality", "unixeng-test"]
        out = self.statustest(command)
        self.matchoutput(out,
                         "Warning: Service afs is already required by "
                         "archetype aquilon. Did you mean to use "
                         "--environment_override?",
                         command)

    def test_102_add_afs_override(self):
        command = ["add_required_service", "--service", "afs",
                   "--archetype", "aquilon", "--personality", "utpers-dev",
                   "--environment_override", "qa"]
        self.noouttest(command)

    def test_105_show_afs(self):
        command = "show service --service afs"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Required for Archetype: aquilon", command)
        self.matchoutput(out,
                         "Required for Personality: unixeng-test Archetype: aquilon",
                         command)
        self.searchoutput(out,
                          r'Required for Personality: utpers-dev Archetype: aquilon\s*'
                          r'Stage: next\s*'
                          r'Environment Override: qa',
                          command)

    def test_105_search_personality(self):
        command = ["search_personality", "--required_service", "afs"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utpers-dev", command)
        self.matchoutput(out, "aquilon/unixeng-test", command)

        command = ["search_personality", "--required_service", "afs",
                   "--environment_override", "qa"]
        out = self.commandtest(command)
        self.matchoutput(out, "aquilon/utpers-dev", command)
        self.matchclean(out, "unixeng-test", command)

        self.noouttest(["search_personality", "--required_service", "afs",
                        "--environment_override", "prod"])

    def test_105_check_personality_proto(self):
        command = ["show_personality", "--personality", "utpers-dev",
                   "--personality_stage", "next", "--format", "proto"]
        personality = self.protobuftest(command, expect=1)[0]
        self.assertEqual(len(personality.required_services), 1)
        self.assertEqual(personality.required_services[0].service, 'afs')
        self.assertEqual(personality.required_services[0].instance, '')
        self.assertEqual(personality.required_services[0].host_environment, 'qa')

    def test_110_add_defaults(self):
        # Setup required services, as expected by the templates.
        for archetype, servicelist in archetype_required.items():
            for service in servicelist:
                self.noouttest(["add_required_service", "--service", service,
                                "--archetype", archetype,
                                "--justification", "tcm=12345678"])

    def test_115_verify_defaults(self):
        all_services = set()
        for archetype, servicelist in archetype_required.items():
            all_services.update(servicelist)

        for archetype, servicelist in archetype_required.items():
            command = ["show_archetype", "--archetype", archetype]
            out = self.commandtest(command)
            for service in servicelist:
                self.matchoutput(out, "Service: %s" % service, command)

            for service in all_services - set(servicelist):
                self.matchclean(out, "Service: %s" % service, command)

    def test_120_add_choosers(self):
        for service in ["chooser1", "chooser2", "chooser3"]:
            command = ["add_required_service", "--service", service,
                       "--archetype=aquilon", "--personality=unixeng-test"]
            self.noouttest(command)

    def test_125_show_personality_current(self):
        command = ["show_personality", "--archetype=aquilon",
                   "--personality=unixeng-test"]
        out = self.commandtest(command)
        self.matchoutput(out, "Stage: current", command)
        self.matchclean(out, "chooser1", command)
        self.matchclean(out, "chooser2", command)
        self.matchclean(out, "chooser3", command)

    def test_125_show_personality_next(self):
        command = ["show_personality", "--archetype=aquilon",
                   "--personality=unixeng-test",
                   "--personality_stage=next"]
        out = self.commandtest(command)
        self.matchoutput(out, "Stage: next", command)
        self.matchoutput(out, "Service: chooser1", command)
        self.matchoutput(out, "Service: chooser2", command)
        self.matchoutput(out, "Service: chooser3", command)

    def test_125_show_personality_next_proto(self):
        command = ["show_personality", "--archetype=aquilon",
                   "--personality=unixeng-test",
                   "--personality_stage=next", "--format", "proto"]
        personality = self.protobuftest(command, expect=1)[0]
        self.assertEqual(personality.archetype.name, "aquilon")
        self.assertEqual(personality.name, "unixeng-test")
        self.assertEqual(personality.stage, "next")
        services = set(item.service for item in personality.required_services)
        self.assertTrue("chooser1" in services)
        self.assertTrue("chooser2" in services)
        self.assertTrue("chooser3" in services)

    def test_125_show_service(self):
        command = "show service --service chooser1"
        out = self.commandtest(command.split(" "))
        self.searchoutput(out,
                          r"Required for Personality: unixeng-test Archetype: aquilon$"
                          r"\s+Stage: next$",
                          command)

    def test_125_show_stage_diff(self):
        command = ["show_diff", "--personality", "unixeng-test",
                   "--archetype", "aquilon",
                   "--personality_stage", "current", "--other_stage", "next"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'missing Required Services in Personality aquilon/unixeng-test@current:$'
                          r'\s*afs$'
                          r'\s*chooser1$'
                          r'\s*chooser2$'
                          r'\s*chooser3$',
                          command)

    def test_125_show_override_diff(self):
        command = ["show_diff", "--archetype", "aquilon",
                   "--personality", "unixeng-test", "--personality_stage", "next",
                   "--other", "utpers-dev", "--other_stage", "next"]
        out = self.commandtest(command)
        self.searchoutput(out,
                          r'matching Required Services with different values:\s*'
                          r'afs value=None, othervalue=qa$',
                          command)

    def test_129_promite_unixeng_test(self):
        self.noouttest(["promote", "--personality", "unixeng-test",
                        "--archetype", "aquilon"])

    def test_130_add_utsvc(self):
        command = ["add_required_service", "--personality=compileserver",
                   "--service=utsvc", "--archetype=aquilon"]
        self.noouttest(command)

    def test_135_verify_utsvc(self):
        command = ["show_personality", "--archetype=aquilon",
                   "--personality=compileserver"]
        out = self.commandtest(command)
        self.matchoutput(out, "Service: utsvc", command)

    def test_140_add_scope_test(self):
        command = ["add_required_service", "--personality=utpers-dev",
                   "--service=scope_test", "--archetype=aquilon"]
        self.noouttest(command)

    def test_145_verify_scope_test(self):
        command = ["show_personality", "--archetype=aquilon",
                   "--personality=utpers-dev",
                   "--personality_stage=next"]
        out = self.commandtest(command)
        self.matchoutput(out, "Service: scope_test", command)

    def test_150_copy_personality(self):
        self.noouttest(["add_personality", "--personality", "required_svc_test",
                        "--eon_id", "2", "--archetype", "aquilon",
                        "--copy_from", "utpers-dev",
                        "--copy_stage", "next",
                        "--host_environment", "dev"])

        command = ["show_personality", "--archetype=aquilon",
                   "--personality=required_svc_test",
                   "--personality_stage=next"]
        out = self.commandtest(command)
        self.matchoutput(out, "Service: scope_test", command)
        self.matchoutput(out, "Stage: next", command)

        self.successtest(["del_personality", "--personality", "required_svc_test",
                          "--archetype", "aquilon"])

    def test_160_add_badservice(self):
        command = ["add_required_service", "--service=badservice",
                   "--personality=badpersonality2", "--archetype=aquilon"]
        self.noouttest(command)

    def test_165_verify_badservice(self):
        command = ["show_personality", "--archetype=aquilon",
                   "--personality=badpersonality2"]
        out = self.commandtest(command)
        self.matchoutput(out, "Service: badservice", command)

    def test_170_add_solaris(self):
        command = ["add_required_service", "--service", "ips",
                   "--archetype", "aquilon", "--osname", "solaris",
                   "--osversion", "11.1-x86_64"]
        self.noouttest(command)

    def test_175_show_os(self):
        command = ["show_os", "--archetype", "aquilon", "--osname", "solaris",
                   "--osversion", "11.1-x86_64"]
        out = self.commandtest(command)
        self.matchoutput(out, "Required Service: ips", command)

    def test_175_show_service(self):
        command = ["show_service", "--service", "ips"]
        out = self.commandtest(command)
        self.matchoutput(out, "Required for Operating System: solaris "
                         "Version: 11.1-x86_64 Archetype: aquilon",
                         command)

    def test_176_copy_os(self):
        command = ["add_os", "--archetype", "aquilon", "--osname", "solaris",
                   "--osversion", "11.2-x86_64", "--copy_version", "11.1-x86_64"]
        self.noouttest(command)

    def test_177_verify_copy(self):
        command = ["show_os", "--archetype", "aquilon", "--osname", "solaris",
                   "--osversion", "11.2-x86_64"]
        out = self.commandtest(command)
        self.matchoutput(out, "Required Service: ips", command)

    def test_178_del_copy(self):
        self.noouttest(["del_os", "--archetype", "aquilon", "--osname", "solaris",
                        "--osversion", "11.2-x86_64"])

    def test_200_archetype_duplicate(self):
        command = "add required service --service afs --archetype aquilon"
        command += " --justification tcm=12345678"
        self.badrequesttest(command.split(" "))

    def test_200_personality_duplicate(self):
        command = ["add_required_service", "--service", "chooser1",
                   "--archetype", "aquilon", "--personality", "unixeng-test"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Service chooser1 is already required by "
                         "personality aquilon/unixeng-test@next.",
                         command)

    def test_200_os_duplicate(self):
        command = ["add_required_service", "--service", "ips",
                   "--archetype", "aquilon", "--osname", "solaris",
                   "--osversion", "11.1-x86_64"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Service ips is already required by operating system "
                         "aquilon/solaris-11.1-x86_64.",
                         command)

    def test_200_missing_service(self):
        command = ["add_required_service", "--service",
                   "service-does-not-exist", "--archetype", "aquilon",
                   "--justification", "tcm=12345678"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Service service-does-not-exist not found.",
                         command)

    def test_200_missing_personality(self):
        command = ["add_required_service", "--service", "afs",
                   "--personality", "personality-does-not-exist",
                   "--archetype", "aquilon"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Personality personality-does-not-exist, "
                         "archetype aquilon not found.",
                         command)

    def test_200_missing_personality_stage(self):
        command = ["add_required_service", "--service", "afs",
                   "--personality", "nostage", "--archetype", "aquilon",
                   "--personality_stage", "previous"]
        out = self.notfoundtest(command)
        self.matchoutput(out,
                         "Personality aquilon/nostage does not have stage "
                         "previous.",
                         command)

    def test_200_bad_personality_stage(self):
        command = ["add_required_service", "--service", "afs",
                   "--personality", "nostage", "--archetype", "aquilon",
                   "--personality_stage", "no-such-stage"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "'no-such-stage' is not a valid personality "
                         "stage.", command)

    def test_200_noncompilable_archetype(self):
        command = ["add_required_service", "--service", "afs",
                   "--archetype", "windows"]
        out = self.unimplementederrortest(command)
        self.matchoutput(out, "Archetype windows is not compileable, "
                         "required services are not supported.", command)

    def test_200_noncompilable_os(self):
        command = ["add_required_service", "--service", "afs",
                   "--archetype", "windows",
                   "--osname", "windows", "--osversion", "nt61e"]
        out = self.unimplementederrortest(command)
        self.matchoutput(out, "Archetype windows is not compileable, "
                         "required services are not supported.", command)

    def test_200_noncompilable_personality(self):
        command = ["add_required_service", "--service", "afs",
                   "--archetype", "windows", "--personality", "generic"]
        out = self.unimplementederrortest(command)
        self.matchoutput(out, "Archetype windows is not compileable, "
                         "required services are not supported.", command)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddRequiredService)
    unittest.TextTestRunner(verbosity=2).run(suite)
