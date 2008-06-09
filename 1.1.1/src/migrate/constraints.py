#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
""" functions for managing Oracle constraints """

from depends import *
import re

def rename_non_null(dbf):
    stmt = """
    SELECT C.constraint_name  con,
           C.table_name       tab,
           C.search_condition cond
      FROM user_constraints C
     WHERE C.constraint_type = 'C'
       AND C.constraint_name LIKE 'SYS%' """

    cons = dbf.safe_execute(stmt)

    rename =[]
    pat = re.compile('\"(.*)\"')

    for i in cons:
        if i[2].endswith('IS NOT NULL'):
            col = pat.match(i[2]).group().strip('"')
            nm = '%s_%s_NN'%(i[1], col)
            rename = 'ALTER TABLE %s RENAME CONSTRAINT %s TO %s'%(i[1],i[0],nm)
            dbf.safe_execute(rename)
