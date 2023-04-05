#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 21:03
@Desc    :

'''

__author__ = "wush"

import time
from typing import Any

import peewee
from peewee import (
    Model,
    BigIntegerField, SmallIntegerField, IntegerField,
    CharField)
from pydantic.utils import GetterDict


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class UserModel(Model):
    id = BigIntegerField(primary_key=True)
    username = CharField(max_length=150, unique=True, index=True, help_text="用户名(登录用户)")
    full_name = CharField(max_length=250, help_text="全名")
    password = CharField(max_length=128, help_text="密码")
    role_key = IntegerField(default=-1, help_text="关联角色id， 默认-1")
    email = CharField(max_length=150, help_text="用户邮箱")
    is_superuser = SmallIntegerField(default=0, help_text="是否超级用户")
    is_active = SmallIntegerField(default=1, help_text="是否正常 (冻结)")
    last_login = BigIntegerField(null=False, default=lambda: int(time.time() * 1000))
    created_by = BigIntegerField(default=-1, help_text="创建人，如果是超级管理员，则为0")
    avatar = CharField(max_length=250, null=True, default=None, help_text="用户头像")
    remark = CharField(max_length=250, default='', help_text="备注")
    create_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)
    update_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)
    md5_pw = CharField(default='', help_text='md5 密码摘要')
    last_reset_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), help_text="用户最近重置时间")

    class Meta:
        table_name = "user"
        getter_dict = PeeweeGetterDict


class RoleModel(Model):
    id = BigIntegerField(primary_key=True)
    role = CharField(max_length=32, unique=True, index=True, help_text="角色名称")
    role_key = CharField(max_length=128, unique=True, null=False, help_text="角色标识")
    description = CharField(max_length=128, null=False, help_text="角色描述")
    created_by = IntegerField(null=False, index=True, help_text="创建人")

    create_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)
    update_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)

    class Meta:
        table_name = "role"
        orm_mode = True
        getter_dict = PeeweeGetterDict


class CasbinObjectModel(Model):
    id = BigIntegerField(primary_key=True)
    object_name = CharField(max_length=128, unique=True, index=True, null=False, help_text="资源名称")
    object_key = CharField(max_length=128, unique=True, index=True, null=False, help_text="资源标识")
    description = CharField(max_length=128, null=False, help_text="资源描述")
    created_by = IntegerField(null=False, index=True, help_text="关联用户id")

    create_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)
    update_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)

    class Meta:
        table_name = "casbin_object"
        orm_mode = True
        getter_dict = PeeweeGetterDict


class CasbinActionModel(Model):
    id = BigIntegerField(primary_key=True)
    action_name = CharField(max_length=128, unique=True, index=True, null=False, help_text="动作名称")
    action_key = CharField(max_length=128, unique=True, index=True, null=False, help_text="动作标识")
    description = CharField(max_length=128, null=False, help_text="动作描述")
    created_by = IntegerField(null=False, index=True, help_text="关联用户id")

    create_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)
    update_time = BigIntegerField(null=False, default=lambda: int(time.time() * 1000), index=True)

    class Meta:
        table_name = "casbin_action"
        orm_mode = True
        getter_dict = PeeweeGetterDict


class CasbinRuleModel(Model):
    id = BigIntegerField(primary_key=True)
    ptype = CharField(max_length=128, null=False, unique=True)
    v0 = CharField(128, null=True)
    v1 = CharField(128, null=True)
    v2 = CharField(128, null=True)
    v3 = CharField(128, null=True)
    v4 = CharField(128, null=True)
    v5 = CharField(128, null=True)

    class Meta:
        table_name = "casbin_rule"
        orm_mode = True
        getter_dict = PeeweeGetterDict


if __name__ == '__main__':
    pass
