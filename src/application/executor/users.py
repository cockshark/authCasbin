#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 20:42
@Desc    :

'''

__author__ = "wush"

from typing import Optional, List, Dict

from email_validator import validate_email

from application.dto.users import CommonUser
from domain.gateway.users import (
    CommonUserManager,
    CommonRoleManager,
    CommonCasbinActionManager)
from infrastructure.log.log import logger
from pkg.verifyUtil import get_password_hash
from public.constants import DEFAULT_PASSWORD


class UsersExecutor:

    def __init__(self):
        self.user_manager = CommonUserManager()
        self.role_manager = CommonRoleManager()
        self.casbin_action_manager = CommonCasbinActionManager()

    async def all_users(self) -> Optional[List[CommonUser]]:
        """
           数据量大可以改成流式查询接口， 使用 pymysql.cursors.SSCursor
        :return:
        """
        return self.user_manager.all_users()

    async def name_all_users(self) -> Optional[Dict[str, dict]]:
        usersInDb = await self.all_users()

        name_users = {user.username: user.dict() for user in usersInDb}

        return name_users

    async def create_superuser(self, username: str = "casbinAdmin") -> None:
        """
        创建超级管理员,和对应的权限
        :param username:
        :return:
        """
        hashed_password = get_password_hash(DEFAULT_PASSWORD)
        if not await self.user_manager.is_user_exist(username):
            logger.debug(f"创建超级管理员 username: casbinadmin")
            await self.create_user(
                username=username,
                full_name=username,
                hash_password=hashed_password,
                email="casbinadmin@akulaku.com",
                remark="超级管理员，拥有所有权限",
                is_superuser=1, is_active=1, created_by=0)

        casbin_admin = await self.user_manager.get_user_by_username(username)

        role_count = await self.role_manager.get_total_role_count()
        if role_count <= 0:
            # 创建角色role
            await self.role_manager.create_role(role="超级管理员",
                                                role_key="role_superadmin",
                                                description="超级管理员，拥有所有的系统权限",
                                                created_by=casbin_admin.id)
            await self.role_manager.create_role(role="管理员",
                                                role_key="role_admin",
                                                description="管理员，拥有大部分系统权限",
                                                created_by=casbin_admin.id)
            await self.role_manager.create_role(role="普通用户",
                                                role_key="role_generaluser",
                                                description="普通用户，默认注册的用户",
                                                created_by=casbin_admin.id)

        casbin_action_count = await self.casbin_action_manager.casbin_action_count()

    async def create_user(
            self,
            username: str,
            full_name: str,
            hash_password: str,
            email: str,
            remark: str = "",
            **kwargs) -> int:
        """

        :param full_name: 全名
        :param username: 用戶名
        :param hash_password: 哈希密碼
        :param email: 郵箱
        :param remark: 备注
        :return: 创建用户的id, 返回0 表示创建失败
        """
        if not validate_email(email):
            logger.error(f"email :{email} EmailSyntaxError !")
            return 0

        return await self.user_manager.create_user(username, full_name, hash_password, email, remark=remark, **kwargs)


if __name__ == '__main__':
    pass
