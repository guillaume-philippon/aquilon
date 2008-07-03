#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""CfgPath formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.configuration import CfgPath


class CfgPathFormatter(ObjectFormatter):
    def format_raw(self, cfg_path, indent=""):
        return indent + "Template: %s" % cfg_path

ObjectFormatter.handlers[CfgPath] = CfgPathFormatter()


#if __name__=='__main__':