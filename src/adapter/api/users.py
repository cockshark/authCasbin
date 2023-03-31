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

from datetime import timedelta
from typing import Annotated, Dict

from fastapi import Request, Body, Depends, status, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm

from adapter.dependencies.users import (
    authenticate_user,
    get_users_from_db,
    create_access_token,
    get_current_active_user,
    get_current_active_user_with_scope,
    get_current_user_with_scope)

"""
users
"""

from adapter.api.fastapiBaseRouter import BaseAPIRouter
from adapter.schema.users import (
    UserListInputDto,
    UserListOutputDto,
    UserListOutputData,
    Token,
    AppTokenConfig, User
)

# from application.executor.users import Users


users_router = BaseAPIRouter(tags=["user"])


######################################
# access_token 系统登陆相关的api接口
######################################

@users_router.post("/token",
                   description="获取token",
                   response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        usersInDb: Annotated[Dict[Dict[str, dict]], Depends(get_users_from_db)]
):
    """
    The scopes parameter receives a dict with each scope as a key and the description as the value:

    """
    user = authenticate_user(usersInDb, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=AppTokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},  # todo remove scopes maybe
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


######################################
# User相关的api接口
######################################

@users_router.get("/users/me/",
                  description="获取当前激活用户",
                  response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@users_router.post('/users/create_user')
async def create_user():
    pass


@users_router.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["items"])]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@users_router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user_with_scope)]):
    return {"status": "ok"}


@users_router.post("/users/list",
                   description="获取用户列表",
                   response_model=UserListOutputDto
                   )
async def user_list(request: Request, body: UserListInputDto = Body(...)):
    users = None
    return UserListOutputDto(data=UserListOutputData)


if __name__ == '__main__':
    pass
