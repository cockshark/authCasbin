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
    UserModel, RoleModel, CasbinActionModel)
from infrastructure.database.mysql import MySQLPersistence


class CommonUserManager:

    def __init__(self):
        self.user_persist = MySQLPersistence(model=UserModel)

    async def all_users(self) -> Optional[List[UserModel]]:
        """

        要处理掉不需要的字段信息
        :return:
        """
        pass

    async def is_user_exist(self, username: str) -> bool:
        pass

    async def create_user(
            self,
            username: str,
            full_name: str,
            hash_password: str,
            email: str,
            remark: str = "",
            **kwargs) -> int:
        pass

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        pass


class CommonRoleManager:
    def __init__(self):
        self.role_persist = MySQLPersistence(model=RoleModel)

    async def get_total_role_count(self) -> int:
        """
        获取 当前表里role一共有多少个
        :return:
        """
        return await self.role_persist.role_count()

    async def create_role(
            self,
            role: str,
            role_key: str,
            description: str,
            created_by: int) -> None:
        await self.role_persist.create_role(role, role_key, description, created_by)


class CommonCasbinActionManager:
    def __init__(self):
        self.casbin_action_persist = MySQLPersistence(model=CasbinActionModel)

    async def casbin_action_count(self):
        return await self.casbin_action_persist.casbin_action_count()


if __name__ == '__main__':
    pass
