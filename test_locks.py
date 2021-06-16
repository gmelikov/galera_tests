#!/usr/bin/env python
# -*-coding: utf-8 -*-
# vim: sw=4 ts=4 expandtab ai
#
# Copyright 2021 George Melikov <mail@gmelikov.ru>
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import mysql.connector
from mysql.connector import errors
import logging
import sys
import unittest


LOG = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


user = 'lock_user_test'
passw = 'lock_password'
db_name = 'lock_tests'

if len(sys.argv) < 4:
    print('I need 3 mysql hosts to work!')
    exit()

host1 = sys.argv.pop(1)
host2 = sys.argv.pop(1)
host3 = sys.argv.pop(1)

link1 = '00047d69-1799-4a4c-ab20-9a74a45d8a01'
link2 = '00047d69-1799-4a4c-ab20-9a74a45d8a02'

endp1 = '00046958-42eb-4c4b-bab9-f2bc16673d01'


cnx1 = mysql.connector.connect(user=user, password=passw,
                               host=host1,
                               database=db_name)
cnx2 = mysql.connector.connect(user=user, password=passw,
                               host=host2,
                               database=db_name)
cnx3 = mysql.connector.connect(user=user, password=passw,
                               host=host3,
                               database=db_name)

cnx1.start_transaction()
cnx2.start_transaction()
cnx3.start_transaction()

c1 = cnx1.cursor()
c2 = cnx2.cursor()
c3 = cnx3.cursor()

link_query = (
    "select * from links where uuid=%s for update"
)

link_query_upd_same = (
    "update links set src_endpoint=src_endpoint where uuid=%s"
)

link_query_upd = (
    "update links set endpoints_hash=endpoints_hash+1 where uuid=%s"
)

endp_query_upd = (
    "update endpoints set port=port+1 where uuid=%s"
)


class TestGaleraLocks(unittest.TestCase):

    def tearDown(self):
        cnx1.rollback()
        cnx2.rollback()
        cnx3.rollback()

    def test_selects_only(self):
        LOG.debug('run cnx1')
        c1.execute(link_query, (link1,))
        c1.fetchall()
        LOG.debug('run cnx2')
        c2.execute(link_query, (link1,))
        c2.fetchall()

        LOG.debug('commit cnx1')
        cnx1.commit()
        LOG.debug('commit cnx2')
        cnx2.commit()

    def test_1_update_same_val_2_select(self):
        LOG.debug('run cnx1')
        c1.execute(link_query, (link1,))
        c1.fetchall()
        LOG.debug('run cnx2')
        c2.execute(link_query, (link1,))
        c2.fetchall()

        LOG.debug('run update cnx1')
        c1.execute(link_query_upd_same, (link1,))
        c1.fetchall()

        LOG.debug('commit cnx1')
        cnx1.commit()
        LOG.debug('commit cnx2')
        cnx2.commit()

    def test_1_update_2_select_deadlock(self):
        LOG.debug('run cnx1')
        c1.execute(link_query, (link1,))
        c1.fetchall()
        LOG.debug('run cnx2')
        c2.execute(link_query, (link1,))
        c2.fetchall()

        LOG.debug('run update cnx1')
        c1.execute(link_query_upd, (link1,))
        c1.fetchall()

        LOG.debug('commit cnx1')
        cnx1.commit()
        LOG.debug('commit cnx2 (should deadlock)')
        with self.assertRaisesRegex(errors.InternalError, 'Deadlock found'):
            cnx2.commit()

    def test_1_select_2_update_deadlock(self):
        LOG.debug('run cnx1')
        c1.execute(link_query, (link1,))
        c1.fetchall()
        LOG.debug('run cnx2')
        c2.execute(link_query, (link1,))
        c2.fetchall()

        LOG.debug('run update cnx2')
        c2.execute(link_query_upd, (link1,))
        c2.fetchall()

        LOG.debug('commit cnx1')
        cnx1.commit()
        LOG.debug('commit cnx2 (should deadlock)')
        cnx2.commit()

    def test_1_update_of_different_raw_2_select(self):
        LOG.debug('run cnx1')
        c1.execute(link_query, (link1,))
        c1.fetchall()
        LOG.debug('run cnx2')
        c2.execute(link_query, (link1,))
        c2.fetchall()

        LOG.debug('run update different raw cnx1')
        c1.execute(link_query_upd, (link2,))
        c1.fetchall()

        LOG.debug('commit cnx1')
        cnx1.commit()
        LOG.debug('commit cnx2')
        cnx2.commit()

    def test_1_update_of_different_table_2_select(self):
        LOG.debug('run cnx1')
        c1.execute(link_query, (link1,))
        c1.fetchall()
        LOG.debug('run cnx2')
        c2.execute(link_query, (link1,))
        c2.fetchall()

        LOG.debug('run update different table cnx1')
        c1.execute(endp_query_upd, (endp1,))
        c1.fetchall()

        LOG.debug('commit cnx1')
        cnx1.commit()
        LOG.debug('commit cnx2')
        cnx2.commit()


if __name__ == '__main__':
    unittest.main()
