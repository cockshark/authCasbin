#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 20:57
@Desc    :

'''

__author__ = "wush"

from typing import Optional, List

from domain.model.users import (
    UserModel,
    RoleModel,
    CasbinActionModel,
    CasbinObjectModel,
    CasbinRuleModel)
from infrastructure.database.mysql import MySQLPersistence
from infrastructure.log.log import logger
from public.error import RoleNotExistError


class CommonUserManager:

    def __init__(self):
        self.user_persist = MySQLPersistence(model=UserModel)

    async def all_users(self) -> Optional[List[UserModel]]:
        """
        todo 要处理掉不需要的字段信息
        :return:
        """
        return await self.user_persist.all()

    async def is_user_exist(self, username: str) -> bool:
        pass

    async def create_user(
            self,
            username: str,
            full_name: str,
            hash_password: str,
            email: str,
            created_by: int,
            remark: str = "",
            **kwargs) -> int:
        is_superuser = kwargs.get("is_superuser", 0)
        is_active = kwargs.get("is_active", 1)
        avatar = kwargs.get("avatar", "")
        return await self.user_persist.add_user(username, full_name, hash_password, role_key=-1, email=email,
                                                is_superuser=is_superuser, is_active=is_active, created_by=created_by,
                                                avatar=avatar, remark=remark)

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        pass

    async def total_user_count(self) -> int:
        return await self.user_persist.count()

    async def get_id_by_username(self, username: str) -> Optional[int]:
        return await self.user_persist.get_id_by_username(username)

    async def get_user_by_id(self, primary_key: int) -> Optional[UserModel]:
        return await self.user_persist.get_model_by_primary_key(primary_key)

    async def get_users_by_fullfuzz_username(self, keyword, offset, limit) -> Optional[List[UserModel]]:
        return await self.user_persist.get_models_by_fullfuzz_username(keyword, offset, limit)

    async def get_many_users(self, offset: int, limit: int) -> Optional[List[UserModel]]:
        return await self.user_persist.get_many_models(offset, limit)

    async def get_users_count_by_fullfuzz_username(self, keyword: str) -> int:
        return await self.user_persist.get_models_count_by_fullfuzz_username(keyword)

    async def update_user_status(self, primary_key: int, is_active: int):
        if is_active >= 1:
            is_active = 1
        return await self.user_persist.update_user_status(primary_key, is_active)

    async def delete_user_by_id(self, primary_key):
        await self.user_persist.delete_user_by_id(primary_key=primary_key)


class CommonRoleManager:
    def __init__(self):
        self.role_persist = MySQLPersistence(model=RoleModel)

    async def total_role_count(self) -> int:
        """
        获取 当前表里role一共有多少个
        :return:
        """
        return await self.role_persist.count()

    async def create_role(
            self,
            role: str,
            role_key: str,
            description: str,
            created_by: int) -> None:
        await self.role_persist.create_role(role, role_key, description, created_by)

    async def get_role_by_key(self, role_key) -> Optional[RoleModel]:
        role = await self.role_persist.get_role_by_key(role_key=role_key)
        if not role:
            raise RoleNotExistError(role_key=role_key)
        return role


class CommonCasbinActionManager:
    def __init__(self):
        self.casbin_action_persist = MySQLPersistence(model=CasbinActionModel)

    async def casbin_action_count(self) -> int:
        return await self.casbin_action_persist.count()

    async def create_casbin_actions(
            self,
            action_names: List[str],
            action_keys: List[str],
            descriptions: List[str],
            created_by: int
    ):
        """
        批量创建 casbin actions
        :param action_names:  CasbinActionModel action name
        :param action_keys:  CasbinActionModel action key
        :param descriptions: CasbinActionModel action desc
        :param created_by: 创建人
        :return:
        """
        assert len(action_names) == len(action_keys) == len(descriptions), "批量创建actions 保证字段长度对齐"

        for action_name, action_key, description in zip(action_names, action_keys, descriptions):
            await self.casbin_action_persist.create_casbin_action(
                action_name, action_key, description, created_by=created_by
            )

    async def all_actions(self) -> List[CasbinActionModel]:
        return await self.casbin_action_persist.all()


class CommonCasbinObjectManager:
    def __init__(self):
        self.casbin_object_persist = MySQLPersistence(model=CasbinObjectModel)

    async def casbin_object_count(self) -> int:
        return await self.casbin_object_persist.count()

    async def create_casbin_objects(
            self,
            object_names: List[str],
            object_keys: List[str],
            descriptions: List[str],
            created_by: int
    ):
        assert len(object_names) == len(object_keys) == len(descriptions), "批量创建objects 保证字段长度对齐"

        for object_name, object_key, description in zip(object_names, object_keys, descriptions):
            await self.casbin_object_persist.create_casbin_object(
                object_name, object_key, description, created_by=created_by
            )

    async def all_objects(self):
        return await self.casbin_object_persist.all()


class CommonCasbinRuleManager:
    def __init__(self):
        self.casbin_rule_persist = MySQLPersistence(model=CasbinRuleModel)

    async def casbin_rule_count(self) -> int:
        return await self.casbin_rule_persist.count()

    async def get_single_rule_by_filter(self, **kwargs) -> Optional[CasbinRuleModel]:
        return await self.casbin_rule_persist.get_rule_by_filter(**kwargs)

    async def add_casbin_rule(self, **kwargs):
        logger.info(f"add_casbin_rule kwargs :{kwargs}")
        await self.casbin_rule_persist.add_casbin_rule(**kwargs)


if __name__ == '__main__':
    pass
