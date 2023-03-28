#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 19:59
@Desc    :

统一用户管理
  - 列表
  - 操作：添加、删除、禁用、启用、编辑
  - 搜索

todo: 依赖权限处理，不是每个用户都有权限进行对应的操作
'''

__author__ = "wush"

from fastapi import Request, Body


"""
users
"""

from adapter.api.fastapiBaseRouter import BaseAPIRouter
from adapter.schema.users import (
    UserListInputDto,
    UserListOutputDto,
    UserListOutputData
)
from application.executor.users import Users

users_router = BaseAPIRouter(tags=["user"])


@users_router.post("/user/list",
                   description="获取用户列表",
                   response_model=UserListOutputDto
                   )
async def user_list(request: Request, body: UserListInputDto = Body(...)):

    users = None
    return UserListOutputDto(data=UserListOutputData)


if __name__ == '__main__':
    pass
