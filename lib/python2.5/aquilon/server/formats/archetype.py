# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Archetype formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import Archetype


class ArchetypeFormatter(ObjectFormatter):
    def format_raw(self, archetype, indent=""):
        details = [ indent + "Archetype: %s" % archetype.name ]
        for item in archetype.service_list:
            details.append(indent + "  Required Service: %s"
                    % item.service.name)
            if item.comments:
                details.append(indent + "    Comments: %s" % item.comments)
        if archetype.comments:
            details.append(indent + "  Comments: %s" % archetype.comments)
        return "\n".join(details)

ObjectFormatter.handlers[Archetype] = ArchetypeFormatter()


