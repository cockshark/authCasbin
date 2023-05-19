#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 20:08
@Desc    :

'''

__author__ = "wush"

from typing import Optional, List

from pydantic import BaseModel, Field, BaseSettings, root_validator

from adapter.schema.baseResponse import ResponseModel
from infrastructure.config.config import system_config


class AppTokenConfig(BaseSettings):
    """
    在终端通过以下命令生成一个新的密匙:
    openssl rand -hex 32
    加密密钥 这个很重要千万不能泄露了，而且一定自己生成并替换。
    """
    SECRET_KEY: str = system_config.secret_key
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # token失效时间


class Token(BaseModel):
    access_token: str
    token_type: str


class GeneralOutputDto(ResponseModel):
    pass


class LogoutOutputDto(ResponseModel):
    pass


class TokenData(BaseModel):
    username: Optional[str] = Field(default=None)
    scopes: List[str] = []


class User(BaseModel):
    user_id: int
    username: str = Field(...)
    email: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=False)  # 是否激活
    password: str = Field()


class Users(BaseModel):
    users: List[User]
    count: int


class Role(BaseModel):
    role: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="角色标识")
    description: str = Field(None, description="角色描述")


class Roles(BaseModel):
    roles: List[Role]
    count: int


class CasbinObject(BaseModel):
    object_name: str
    object_key: str
    description: str


class CasbinObjects(BaseModel):
    casbin_objects: List[CasbinObject]
    count: int


class CasbinAction(BaseModel):
    action_name: str
    action_key: str
    description: str


class CasbinActions(BaseModel):
    casbin_actions: List[CasbinAction]
    count: int


class UserCreateInputDto(User):
    password: str = Field(...)
    current_user: str = Field(..., description="當前用戶")
    avatar: Optional[str] = Field(None, description="用户头像")
    remark: str = Field(default="", description="备注")


class UserCreateOutputDto(ResponseModel):
    pass


class UpdateUserDto(BaseModel):
    user_id: int
    username: str
    fullname: str
    password: Optional[str] = Field(default="")
    email: str
    avatar: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)


class UserListInputDto(BaseModel):
    pass


class UserListOutputData(BaseModel):
    """
        todo: 展示用户的关键字段信息
    """
    pass


class UserListOutputDto(ResponseModel):
    data: Optional[List[UserListOutputData]]


class UpdateUserRoleDto(BaseModel):
    user_id: int
    roles: List[str] = Field(description="角色名称")


class UserRolesOutputData(BaseModel):
    options: List[str] = Field(description="所有权限组的名称")
    checkeds: List[str] = Field(description="当前用户所拥有的用户组")


class UserRolesOutputDto(ResponseModel):
    data: UserRolesOutputData


class CreateRoleInputDto(Role):
    user_id: int = Field(..., description="created_by,创建人")


class UpdateRoleInputDto(BaseModel):
    role_id: int = Field(gt=0)
    role: str
    role_key: str
    description: str


class RoleCasbinOutputData(BaseModel):
    options: List[List[str]] = Field(description="所有权限组的名称")
    checkeds: List[List[str]] = Field(description="当前用户所拥有的用户组")

    @root_validator(pre=True)
    def combine_data(cls, values):
        import copy
        options = values.get("options")
        checkeds = values.get("checkeds")

        ops = copy.deepcopy(options)

        for checked in checkeds:
            if len(checked) == 0:
                break
            for op in ops:
                if checked[0] == op[0]:
                    ops[ops.index(checked)] = checked

        for op in ops:
            if op not in checkeds:
                ops[ops.index(op)] = []

        return values


class RoleCasbinOutputDto(ResponseModel):
    data: RoleCasbinOutputData


class ChangeRoleCasbinRuleInputDto(BaseModel):
    role_id: int
    checkeds: List[List[str]] = Field(..., description="用户组权限说明列表")


class CreateCasbinObjectInputDto(BaseModel):
    name: str
    object_key: str
    description: str


class UpdateCasbinObjectInputDto(BaseModel):
    co_id: int
    name: str
    object_key: str
    description: str


class CreateCasbinActionInputDto(BaseModel):
    name: str
    action_key: str
    description: str


class UpdateCasbinActionInputDto(BaseModel):
    ca_id: int
    name: str
    action_key: str
    description: str


class AuthenticationInputDto(BaseModel):
    obj: str
    action: str


if __name__ == '__main__':
    pass
