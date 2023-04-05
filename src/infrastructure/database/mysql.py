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

    async def all(self):
        return await self.objects.execute(self.model.select())

    async def count(self) -> int:
        return await self.objects.execute(self.model.select().count())

    ###################################
    #             user                #
    ###################################

    async def user_count(self) -> int:
        return await self.objects.execute(self.model.select().count())

    ###################################
    #             role                #
    ###################################

    # async def role_count(self) -> int:
    #     return await self.objects.execute(self.model.select().count())

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

    async def is_role_exist_by_key(self, role_key: str) -> bool:
        role_id = await self.objects.execute(self.model.select(self.model.id).where(
            self.model.role_key == role_key
        ))
        return role_id > 0

    async def get_role_by_key(self, role_key: str):
        return await self.objects.execute(self.model.select().where(self.model.role_key == role_key))

    ###################################
    #             casbin_action       #
    ###################################

    # async def casbin_action_count(self) -> int:
    #     return await self.objects.execute(self.model.select().count())

    async def create_casbin_action(self, action_name: str, action_key: str, description: str, created_by: int) -> None:
        await self.objects.execute(self.model.insert(
            action_name=action_name,
            action_key=action_key,
            description=description,
            created_by=created_by
        ))

    # def get_all_actions(self):
    #     return await self.objects.execute(self.model.select())

    ###################################
    #             casbin_object       #
    ###################################

    # async def casbin_object_count(self) -> int:
    #     return await self.objects.execute(self.model.select().count())

    async def create_casbin_object(self, object_name: str, object_key: str, description: str, created_by: int) -> None:
        await self.objects.execute(self.model.insert(
            object_name=object_name,
            object_key=object_key,
            description=description,
            created_by=created_by
        ))

    # def get_all_objects(self):
    #     return await self.objects.execute(self.model.select())

    ###################################
    #             casbin_rule         #
    ###################################

    # async def casbin_rule_count(self) -> int:
    #     return await self.objects.execute(self.model.select().count())

    async def get_rule_by_filter(self, **kwargs):
        return await self.objects.execute(self.model.select().where(**kwargs).first())

    async def get_rules_by_filter(self, **kwargs):
        return await self.objects.execute(self.model.select().where(**kwargs))

    async def add_casbin_rule(self, **kwargs):
        await self.objects.execute(self.model.insert(**kwargs))
