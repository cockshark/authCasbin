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

import random
from typing import Optional, List, Dict

from email_validator import validate_email

from application.dto.users import CommonUser, CommonRole
from domain.gateway.users import (
    CommonUserManager,
    CommonRoleManager,
    CommonCasbinActionManager,
    CommonCasbinObjectManager,
    CommonCasbinRuleManager)
from infrastructure.log.log import logger
from pkg.verifyUtil import get_password_hash
from public.constants import DEFAULT_PASSWORD
from public.error import RoleNotExistError


class UsersExecutor:

    # todo 所有数据要进行dto处理，去掉一些不必要的信息

    def __init__(self):

        self.user_manager = CommonUserManager()
        self.role_manager = CommonRoleManager()
        self.casbin_action_manager = CommonCasbinActionManager()
        self.casbin_object_manager = CommonCasbinObjectManager()
        self.casbin_rule_manager = CommonCasbinRuleManager()

    """
        user
    """

    async def create_start_data(self):
        """
            第一次执行的时候， 造一些数据
        :return:
        """
        await self._create_superuser()

    async def all_users(self) -> Optional[List[CommonUser]]:
        """
           数据量大可以改成流式查询接口， 使用 pymysql.cursors.SSCursor
        :return:
        """
        return await self.user_manager.all_users()

    async def name_all_users(self) -> Optional[Dict[str, dict]]:
        usersInDb = await self.all_users()

        name_users = {user.username: user.dict() for user in usersInDb}

        return name_users

    async def _create_tmp_users(self):
        """
        创建一下普通的角色用于测试
        :return:
        """
        password = DEFAULT_PASSWORD
        # 普通用户角色
        role_generaluser = await self.role_manager.get_role_by_key(role_key="role_generaluser")

        user_count = await self.user_manager.total_user_count()
        if user_count <= 1:
            for i in range(66):
                is_active = random.randint(0, 1)
                username = "generaluser" + str(i)
                email = "generaluser" + str(i) + "@akulaku.com"
                await self.create_user(username=username, full_name=username,
                                       password=password, email=email,
                                       current_user="casbinAdmin",
                                       remark="我是用于测试的临时创造的普通用户", is_active=is_active)
                # 增加policy
                await self.set_role_casbin_rule(ptype="g", v0=username, v1=role_generaluser.role_key)

    async def get_user_by_id(self, primary_key: int):
        return await self.user_manager.get_user_by_id(primary_key)

    async def get_user_by_username(self, username: str):
        return await self.user_manager.get_user_by_username(username)

    async def get_users_by_keyword(self, keyword: str, offset: int, limit: int):
        if keyword:
            return await self.user_manager.get_users_by_fullfuzz_username(keyword, offset, limit)

        return await self.user_manager.get_many_users(offset, limit)

    async def get_total_amount_by_keyword(self, keyword: str) -> int:
        if keyword:
            return await self.user_manager.get_users_count_by_fullfuzz_username(keyword=keyword)

        return await self.user_manager.total_user_count()

    async def change_user_status_reverse(self, user_id: int):
        user = await self.user_manager.get_user_by_id(user_id)
        if user.is_active:
            logger.warning(f"freeze user {user.username}")
            await self.user_manager.update_user_status(primary_key=user_id, is_active=0)
            return

        await self.user_manager.update_user_status(primary_key=user_id, is_active=1)

    async def delete_user_by_id(self, primary_key: int):
        await self.user_manager.delete_user_by_id(primary_key)

    async def update_user_baseInfo(self,
                                   user_id: int,
                                   username: str = '',
                                   fullname: str = '',
                                   email: str = '',
                                   avatar: str = '',
                                   remark: str = '',
                                   password: str = ''):
        if password != '':
            hashed_password = get_password_hash(password)
        else:
            hashed_password = None

        user = await self.user_manager.get_user_by_id(primary_key=user_id)

        # 处理数据， 空数据不进行更新
        user.username = username if username != '' else user.username
        user.fullname = fullname if fullname != '' else user.fullname
        user.email = email if email != '' else user.email
        user.avatar = avatar if avatar != '' else user.avatar
        user.remark = remark if remark != '' else user.remark
        user.password = hashed_password if hashed_password else user.password

        await self.user_manager.update_user_info_by_userid(
            user_id=user_id,
            username=user.username,
            fullname=user.full_name,
            email=user.email,
            avatar=user.avatar,
            remark=user.remark,
            password=user.password)

    async def create_user(
            self,
            username: str,
            full_name: str,
            password: str,
            email: str,
            current_user: str,
            remark: str = "",
            **kwargs) -> int:
        """

        :param current_user:  當前用戶用戶名
        :param password: 密碼
        :param full_name: 全名
        :param username: 用戶名
        :param email: 郵箱
        :param remark: 备注
        :return: 创建用户的id, 返回0 表示创建失败
        """
        validate_email(email)
        current_user_id = await self.user_manager.get_id_by_username(current_user)
        if not current_user_id:
            current_user_id = -1

        hash_password = get_password_hash(password)
        return await self.user_manager.create_user(username, full_name, hash_password, email,
                                                   created_by=current_user_id, remark=remark, **kwargs)

    async def _create_superuser(self, username: str = "casbinAdmin") -> None:
        """
        创建超级管理员,和对应的权限
        :param username:
        :return:
        """
        password = DEFAULT_PASSWORD
        if not await self.user_manager.is_user_exist(username):
            logger.debug(f"创建超级管理员 username: casbinAdmin")
            await self.create_user(
                username=username,
                full_name=username,
                password=password,
                email="casbinadmin@akulaku.com",
                current_user="system",
                remark="超级管理员，拥有所有权限",
                is_superuser=1, is_active=1, created_by=0)

        casbin_admin = await self.user_manager.get_user_by_username(username)

        role_count = await self.role_manager.total_role_count()
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
        if casbin_action_count <= 0:
            # 创建CasbinAction
            action_names = ["增", "删", "改", "查", "显"]
            action_keys = ["create", "delete", "update", "read", "show"]
            descriptions = ["增加数据", "删除数据", "更新数据", "读取或查询数据", "数据相关组件的显示"]
            created_by = casbin_admin
            await self.casbin_action_manager.create_casbin_actions(action_names, action_keys, descriptions, created_by)

        casbin_object_count = await self.casbin_object_manager.casbin_object_count()
        if casbin_object_count <= 0:
            # 创建CasbinObject
            object_names = ["用户管理", "角色管理", "资源管理", "动作管理"]
            object_keys = ["User", "Role", "CasbinObject", "CasbinAction"]
            descriptions = ["User表--用户相关权限", "Role--角色相关权限", "CasbinObject--资源相关权限",
                            "CasbinAction表--动作相关权限"]
            created_by = casbin_admin
            await self.casbin_object_manager.create_casbin_objects(object_names, object_keys, descriptions, created_by)

        casbin_rule_count = await self.casbin_rule_manager.casbin_rule_count()
        if casbin_rule_count <= 0:
            logger.info("》》》》》》》》》》》》设置用户（组）权限 》》》》》》》》》》》")
            # 超级管理员角色
            role_superadmin = await self.role_manager.get_role_by_key(role_key="role_superadmin")
            # 普通用户角色
            role_generaluser = await self.role_manager.get_role_by_key(role_key="role_generaluser")

            all_casbin_actions = await self.casbin_action_manager.all_actions()
            all_casbin_objects = await self.casbin_object_manager.all_objects()

            # 设置 超级管理员角色 policy 所有权限
            await self.set_role_casbin_rules(role_superadmin, all_casbin_actions, all_casbin_objects)

            # 设置 普通角色 policy, 读取和显示
            await self.set_role_casbin_rules(
                role_generaluser,
                casbin_actions=["read", "show"],
                casbin_objects=all_casbin_objects)

            # 设置超级管理员
            await self.set_role_casbin_rule(ptype="g", v0=casbin_admin.username, v1=role_superadmin.role_key)

            # 自动生成一些普通用户
            await self._create_tmp_users()

    """
        role
    """

    async def get_role_by_role_key(self, role_key: str) -> Optional[CommonRole]:

        try:
            role = await self.role_manager.get_role_by_key(role_key)
        except RoleNotExistError as e:
            logger.error(e.error_msg)
            return None
        else:
            return CommonRole(role_key=role.id)

    async def update_user_role(self, user_id: int, roles: List[str]):

        user = await self.get_user_by_id(user_id)
        casbin_rules = await self.casbin_rule_manager.get_rules_by_filter(ptype="g", v0=user.username)
        if len(casbin_rules) > 0:
            await self.delete_p_casbin_rules(username=user.username)

    """
        casbin rule
    """

    async def delete_p_casbin_rules(self, username: str):
        """
        删除该用户所拥有的所有的用户组role
        :param username:
        :return:
        """

        await self.casbin_rule_manager.delete_p_casbin_rules(ptype="g", v0=username)

    async def set_role_casbin_rules(self, role, casbin_actions, casbin_objects):

        """
            为角色赋能

        因为前端添加policy都是多条,所以接口只暴露批量添加.
        添加policy到数据表中,如果有相同的policy,则不再继续添加.
        :param role: 角色
        :param casbin_actions: 动作权限
        :param casbin_objects:  资源个体列表
        :return: None
        """
        for cos in casbin_objects:
            for cas in casbin_actions:
                await self.set_role_casbin_rule(ptype="p", v0=role.role_key, v1=cos.object_key, v2=cas.action_key)

    async def set_role_casbin_rule(self, ptype: str, **kwargs) -> int:
        """

        :param ptype: p or g
        :param kwargs: v0,v1,v2,v3,v4,v5  一个或者多个
        :return:
        """
        k = 0
        if await self.filter_casbin_rule(ptype, **kwargs):
            k += 1
        else:
            await self._add_casbin_rule(ptype, **kwargs)

        return k

    async def filter_casbin_rule(self, ptype: str, **kwargs):
        """
        查询是否存在相同的policy
        :param ptype:  p or g
        :param kwargs: v0,v1,v2,v3,v4,v5  一个或者多个
        :return:
        """
        return await self.casbin_rule_manager.get_single_rule_by_filter(ptype, **kwargs)

    async def _add_casbin_rule(self, ptype: str, **kwargs):
        """

        :param ptype:
        :param kwargs:
        :return:
        """
        kwargs.update({"ptype": ptype})
        await self.casbin_rule_manager.add_casbin_rule(**kwargs)


if __name__ == '__main__':
    pass
