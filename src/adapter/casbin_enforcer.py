#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   casbin_enforcer.py
@Time    :   2023/4/11 18:54
@Desc    :

'''

__author__ = "wush"

import casbin
import casbin_peewee_adapter
from peewee import MySQLDatabase

from conf import RBAC_MODEL_CONF
from infrastructure.config.config import system_config

db_config = system_config.risk_mysql_cfg  # type: dict

# 创建一个 Peewee 数据库对象
database = MySQLDatabase(
    db_config.pop("database"),
    **db_config
)

adapter = casbin_peewee_adapter.Adapter(database)


def get_casbin_e():
    """
    返回一個 enforcer
    :return:
    """

    return casbin.Enforcer(str(RBAC_MODEL_CONF), adapter)


if __name__ == '__main__':
    e = get_casbin_e()
    print(e.get_roles_for_user(name="casbinAdmin"))
