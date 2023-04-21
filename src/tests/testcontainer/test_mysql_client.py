#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   test_mysql_client.py
@Time    :   2023/4/21 16:21
@Desc    :

'''

__author__ = "wush"

import sqlalchemy

from testcontainers.mysql import MySqlContainer


def test_mysql_engine_mock():
    with MySqlContainer('mysql:127.0.0.1') as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("select version()"))
            version, = result.fetchone()


if __name__ == '__main__':
    pass
