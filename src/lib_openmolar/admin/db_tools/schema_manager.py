#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import os
import hashlib
import logging
from lib_openmolar.common import SETTINGS
from lib_openmolar.admin.db_orm import *

class SchemaManager(object):
    _bare_sql = None
    _md5 = None

    @property
    def CURRENT_SQL(self):
        '''
        the Sql applied to create the current schema
        '''
        if self._bare_sql is None:
            logging.debug("grabbing CURRENT_SQL")
            self._bare_sql = ""

            klasses = SETTINGS.OM_TYPES.values()
            for module in ADMIN_MODULES:
                klasses.append(module.SchemaGenerator())

            for klass in klasses:
                for query in klass.creation_queries:
                    self._bare_sql += query
                    self._bare_sql += ";\n\n"

            for queries in (
                om_views.FUNCTION_SQLS,
                om_views.VIEW_SQLS,
                om_views.RULE_SQLS):
                for query in queries:
                    self._bare_sql += query
                    self._bare_sql += ";\n\n"

        return self._bare_sql

    @property
    def MD5(self):
        logging.debug("getting MD5 sum for the schema")
        if self._md5 is None:
            self._md5 = hashlib.md5(self.CURRENT_SQL).hexdigest()
        logging.debug("MD5 sum is '%s'"% self._md5)
        return self._md5

    def match(self, filepath):
        if not os.path.isfile(filepath):
            return False
        f = open(filepath)
        saved_md5 = hashlib.md5(f.read()).hexdigest()
        f.close()
        result = saved_md5 == self._md5
        logging.debug("saved schema is current? %s"% result)
        return result

    def write(self, filepath):
        f = open(filepath, "w")
        f.write(self.CURRENT_SQL)
        f.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    s = SchemaManager()
    s.MD5
    FILEPATH = "../../../../misc/server/blank_schema.sql"
    #s.write(FILEPATH)
    s.match(FILEPATH)