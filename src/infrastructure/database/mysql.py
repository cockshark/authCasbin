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

在这里只做model 注入
'''

__author__ = "wush"

from peewee import Model
from peewee_async import Manager

from infrastructure.client.mysql import RiskDbConn


class MySQLPersistence:

    def __init__(self, model, client=RiskDbConn) -> None:
        self.model = model  # type: Model
        self.model._meta.database = client.pool  # 注入pool
        self.objects = Manager(self.model._meta.database)

    ###################################
    #             user                #
    ###################################

    async def create_temp_users(self) -> None:
        pass

    ###################################
    #             role                #
    ###################################

    async def role_count(self) -> int:
        return await self.objects.execute(self.model.Select().count())

    async def create_role(self,
                          role: str,
                          role_key: str,
                          description: str,
                          created_by: int) -> None:
        await self.objects.execute(self.model.insert(
            role=role,
            role_key=role_key,
            description=description,
            created_by=created_by
        ))

    ###################################
    #             casbin_action       #
    ###################################

    async def casbin_action_count(self):
        await self.objects.execute(self.model.Select().count())


if __name__ == '__main__':
    pass
