#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 20:48
@Desc    :

'''

__author__ = "wush"

from typing import Optional

from pydantic import BaseModel, Field


class CommonUser(BaseModel):
    """
    对应数据库的关键字段
    """

    username: str = Field(...)
    email: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=False)


class CommonRole(BaseModel):
    role_key: str = Field(description="角色标识")
    role: str = Field(description="角色名称")
    description: str = Field(default="", description="角色描述")


class CommonCasbinRule(BaseModel):
    ptype: str = Field(default=None)
    v0: str = Field(default=None)
    v1: str = Field(default=None)
    v2: str = Field(default=None)
    v3: str = Field(default=None)
    v4: str = Field(default=None)
    v5: str = Field(default=None)


class CommonCasbinObject(BaseModel):
    object_name: str
    object_key: str
    description: str
    created_by: int


class CommonCasbinAction(BaseModel):
    action_name: str = Field()
    action_key: str = Field()
    description: str = Field(default="")
    created_by: int = Field(...)


if __name__ == '__main__':
    pass
