#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

'''
Provides StaticFillsDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "static_fills"

class FillRecord(InsertableRecord):
    def __init__(self):
        InsertableRecord.__init__(self, SETTINGS.psql_conn, TABLENAME)

    @property
    def tooth_id(self):
        return self.value('tooth').toInt()[0]

    @property
    def surfaces(self):
        return str(self.value('surfaces').toString())

    @property
    def material(self):
        return str(self.value('material').toString())

    @property
    def comment(self):
        return unicode(self.value('comment').toString())


class StaticFillsDB(object):
    '''
    class to get static chart information
    '''
    def __init__(self, patient_id):
        #:
        self.patient_id = patient_id
        #:
        self.record_list = []
        self._orig_record_list = []

        query = '''select tooth, surfaces, material, comment
        from %s where patient_id=?'''% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            new = FillRecord()
            QtSql.QSqlQuery.__init__(new, record)

            ## make a copy (a marker of database state)
            orig = QtSql.QSqlRecord()
            QtSql.QSqlQuery.__init__(orig, record)

            #self.record_list.append(record)
            self.record_list.append(new)
            self._orig_record_list.append(orig)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        return self.record_list

    def is_dirty_record(self, i):
        return self.record_list[i] != self._orig_record_list[i]

    @property
    def is_dirty(self):
        if len(self.record_list) != len(self._orig_record_list):
            return True
        is_dirty = False
        for i in range(len(self.record_list)):
            is_dirty = is_dirty or self.is_dirty_record(i)
        return is_dirty

    def commit_changes(self):
        if not self.is_dirty:
            return
        for record in self.record_list:
            if not record in self._orig_record_list:
                query, values = record.insert_query

                q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
                q_query.prepare(query)
                for value in values:
                    q_query.addBindValue(value)
                if q_query.exec_():
                    self._orig_record_list.append(record)
                else:
                    print q_query.lastError().text()
                    SETTINGS.psql_conn.emit_caught_error(q_query.lastError())


    def add_filling_records(self, fill_list):
        '''
        fill_list is a generator of ToothData types
        '''
        for fill in fill_list:
            new = FillRecord()
            new.setValue("patient_id", self.patient_id)
            new.setValue("tooth", fill.tooth_id)
            new.setValue("material", fill.material)
            new.setValue("surfaces", fill.surfaces)
            new.setValue("comment", fill.comment)
            new.remove(new.indexOf('date_charted'))

            self.record_list.append(new)
            fill.in_database = True

if __name__ == "__main__":

    class Duck(object):
        def __init__(self):
            pass

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    object = StaticFillsDB(1)
    restorations = object.records

    print object.is_dirty
    restorations[0].setValue('surfaces', "MODB")
    print object.is_dirty

    print "%d records.. let's add two more"% len(object.records)


    tooth = Duck()
    tooth.tooth_id = 1
    duckfill = Duck()
    duckfill.tooth_id = tooth.tooth_id
    duckfill.tooth = tooth
    duckfill.material = "AM"
    duckfill.surfaces = "MOD"
    duckfill.comment = "I'm new!"

    duckfill2 = Duck()
    duckfill2.tooth_id = tooth.tooth_id
    duckfill2.tooth = tooth
    duckfill2.material = "CO"
    duckfill2.surfaces = "MOD"
    duckfill2.comment = "I am also new"
    object.add_filling_records([duckfill, duckfill2])

    print "%d records"% len(object.records)

    for record in object.records:
        print record.value("material").toString(),
        print record.value("surfaces").toString(),
        print record.value("comments").toString()
