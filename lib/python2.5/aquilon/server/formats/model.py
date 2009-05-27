# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Model formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.model import Model


class ModelFormatter(ObjectFormatter):
    def format_raw(self, model, indent=""):
        details = [indent + "Vendor: %s Model: %s" %
                            (model.vendor.name, model.name)]
        details.append(indent + "  Type: %s" % model.machine_type)
        if model.comments:
            details.append(indent + "  Comments: %s" % model.comments)
        if model.machine_specs:
            details.append(self.redirect_raw(model.machine_specs, indent+"  "))
        return "\n".join(details)

ObjectFormatter.handlers[Model] = ModelFormatter()
