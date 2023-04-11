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

from casbin import Enforcer
from fastapi import (
    Request, Response, Body, Depends,
    status, HTTPException, Security)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import Field

from adapter.casbin_enforcer import get_casbin_e
from adapter.dependencies.users import (
    authenticate_user,
    get_users_from_db,
    create_access_token,
    get_current_active_user,
    get_current_active_user_with_scope,
    get_current_user_with_scope)
from adapter.schema.users import LogoutOutputDto, Users, GeneralOutputDto
from public.error import CredentialsException

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

from adapter.schema.users import (
    UserCreateInputDto,
    UserCreateOutputDto
)

from application.executor.users import UsersExecutor

users_router = BaseAPIRouter(tags=["user"])


######################################
# access_token 系统登陆相关的api接口
######################################

@users_router.post("/login", description="登录")
@users_router.post("/token",
                   description="获取token，登录",
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
    # todo set redis
    return Token(access_token=access_token, token_type="bearer")


@users_router.post("/logout",
                   description="退出登录",
                   response_model=LogoutOutputDto)
async def logout(request: Request, response: Response):
    """
        登出，前端实现redirect 到 login  或者游客首页
    :param request:
    :param response:
    :return:
    """
    # todo remove redis token ,destroy token
    return LogoutOutputDto(success=True)


######################################
# User相关的api接口
######################################

@users_router.get("/user/me/",
                  description="获取当前激活用户",
                  response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@users_router.post('/user/create_user',
                   description="创建用户",
                   status_code=status.HTTP_201_CREATED,
                   name="user create:create",
                   response_model=UserCreateOutputDto)
async def create_user(request: Request,
                      current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["items"])],
                      executor: UsersExecutor,
                      body: UserCreateInputDto = Body(...)):
    """
    注册用户名称不能与用户组的role_key重复
    """
    if executor.get_role_by_role_key(body.username):
        raise CredentialsException(detail="用户名称重复!", headers={"WWW-Authenticate": "Bearer"})

    await executor.create_user(username=body.username, full_name=body.full_name,
                               password=body.password, email=body.email, current_user=current_user.username,
                               remark=body.remark, avatar=body.avatar)
    return UserCreateOutputDto(success=True)


@users_router.get("/user/me/items/",
                  description="获取当前用户资料")
async def read_own_items(
        current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["items"])]
):
    return current_user


@users_router.get("/user/id", description="根据用户id获取用户资料", response_model=User)
async def get_user_by_id(request: Request,
                         current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                         executor: UsersExecutor,
                         e: Enforcer = Depends(get_casbin_e),
                         user_id: int = Field(default=0, gt=0, description="数据库主键，必须大于0")
                         ):
    """

    :param executor:
    :param user_id:数据库主键id
    :param e: Enforcer
    :param request:
    :param current_user: 需要校验当前用户是否是 active， 也要通过casbin校验权限
    :return:
    """

    enforce = e.enforce(current_user.username, "User", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    target = await executor.get_user_by_id(primary_key=user_id)

    return User(**target)


@users_router.get("/user/get_users",
                  description="一次性获取多个用户",
                  response_model=Users)
async def get_users(request: Request,
                    current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                    executor: UsersExecutor,
                    e: Enforcer = Depends(get_casbin_e),
                    offset: int = Field(default=0, alias="skip"),
                    limit: int = Field(default=10),
                    keyword: str = Field(default="")
                    ):
    """
    获取最新的几个用户，倒叙
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param offset: offset
    :param limit:
    :param keyword:
    :return:
    """
    enforce = e.enforce(current_user.username, "User", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    users = await executor.get_users_by_keyword(keyword, offset, limit)
    count = await executor.get_total_amount_by_keyword(keyword)

    return Users(users=users, count=count)


@users_router.get("/user/update_status",
                  description="激活，冻结用户",
                  response_model=GeneralOutputDto)
async def update_user_status(request: Request,
                             current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                             executor: UsersExecutor,
                             e: Enforcer = Depends(get_casbin_e),
                             user_id: int = Field(default=0, gt=0, description="数据库主键，必须大于0")
                             ):
    enforce = e.enforce(current_user.username, "User", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.change_user_status_reverse(user_id)

    return GeneralOutputDto()


@users_router.get("/user/delete_user", description="删除用户", response_model=GeneralOutputDto)
async def delete_single_user(request: Request,
                             current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                             executor: UsersExecutor,
                             e: Enforcer = Depends(get_casbin_e),
                             user_id: int = Field(default=0, gt=0, description="数据库主键，必须大于0")
                             ):
    enforce = e.enforce(current_user.username, "User", "delete")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.delete_user_by_id(user_id)

    return GeneralOutputDto()


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
