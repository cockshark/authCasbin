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

from typing import Optional

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

    # async def user_count(self) -> int:
    #     return await self.objects.execute(self.model.select().count())

    async def get_id_by_username(self, username: str) -> Optional[int]:
        return await self.objects.execute(self.model.select(self.model.id).where(self.model.username == username))

    async def get_user_by_username(self, username: str):
        return await self.objects.execute(self.model.select().where(self.model.username == username))

    async def get_user_by_fullname(self, fullname: str):
        return await self.objects.execute(self.model.select().where(self.model.fullname == fullname))

    async def get_model_by_primary_key(self, primary_key: int):
        return await self.objects.execute(self.model.select().where(self.model.id == primary_key))

    async def get_models_by_fullfuzz_username(self, fullfuzz: str, offset: int, limit: int):
        return await self.objects.execute(
            self.model.select().where(self.model.username.contains(fullfuzz))
            .order_by(self.model.id).offset(offset).limit(limit))

    async def get_models_count_by_fullfuzz_username(self, fullfuzz: str) -> int:
        return await self.objects.execute(
            self.model.select().where(self.model.username.contains(fullfuzz)).count())

    async def get_many_models(self, offset: int, limit: int):
        return await self.objects.execute(self.model.select().order_by(self.model.id).offset(offset).limit(limit))

    async def update_user_status(self, primary_key: int, is_active: int):
        await self.objects.execute(
            self.model.update(self.model.is_active == is_active).where(self.model.id == primary_key))

    async def update_user_info(self, user_id: int, **kwargs):
        await self.objects.execute(self.model.update(**kwargs).where(self.model.id == user_id))

    async def delete_user_by_id(self, primary_key: int):
        """
        这里需要自己指定根据什么删除，且只允许删除一个，且键位必须是unique
        :param primary_key:
        :param kwargs:
        :return:
        """
        await self.objects.execute(self.model.delete().where(self.model.id == primary_key))

    async def add_user(
            self,
            username: str,
            full_name: str,
            password: str,
            role_key: int,
            email: str,
            is_superuser: int,
            is_active: int,
            created_by: int,
            avatar: str,
            remark: str):
        return await self.objects.execute(self.model.insert(
            username=username,
            full_name=full_name,
            password=password,
            role_key=role_key,
            email=email,
            is_superuser=is_superuser,
            is_active=is_active,
            created_by=created_by,
            avatar=avatar,
            remark=remark
        ))

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

    async def delete_casbin_rule(self, **kwargs):
        await self.objects.execute(self.model.delete().where(**kwargs))
