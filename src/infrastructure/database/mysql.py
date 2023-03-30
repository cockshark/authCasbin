#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   mysql.py
@Time    :   2023/3/16 13:24
@Desc    :
MySQL 实现的数据持久化
Infrastructure 层中接口方法的实现都需要将结果的数据对象转化成 Domain 层 model 返回，
因为领域网关 gateway 中定义的接口方法的入参、出参只能包含同层的 model，不可以有外层的数据类型。

'''

__author__ = "wush"

from peewee import Model

from infrastructure.client.mysql import RiskDbConn


class MySQLPersistence:

    def __init__(self, model: Model, client=RiskDbConn) -> None:
        self.model = model
        self.model._meta.database = client.pool  # 注入pool

    def create_superuser(self, username: str = "casbinAdmin") -> None:
        pass

    def create_temp_users(self) -> None:
        pass


if __name__ == '__main__':
    pass
