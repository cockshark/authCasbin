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
from typing import Annotated

from casbin import Enforcer
from fastapi import (
    Request, Response, Body, Depends,
    status, HTTPException, Security)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import Field

from adapter.casbin_enforcer import get_casbin_e
from adapter.dependencies.users import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_active_user_with_scope,
    get_current_user_with_scope)
from adapter.schema.users import (
    LogoutOutputDto,
    Users,
    GeneralOutputDto,
    UpdateUserDto, RoleCasbinOutputDto, RoleCasbinOutputData, ChangeRoleCasbinRuleInputDto)
from public.error import CredentialsException

"""
users
"""

from adapter.api.fastapiBaseRouter import BaseAPIRouter
from adapter.schema.users import (
    UserListInputDto,
    UserListOutputDto,
    Token,
    AppTokenConfig, User
)

from adapter.schema.users import (
    UserCreateInputDto,
    UserCreateOutputDto
)

from adapter.schema.users import (
    UserRolesOutputDto,
    UserRolesOutputData,
    Roles, Role,
    CreateRoleInputDto, UpdateRoleInputDto, CreateCasbinActionInputDto
)

from adapter.schema.users import (
    CasbinObjects, CasbinObject,
    CreateCasbinObjectInputDto,
    UpdateCasbinObjectInputDto,
    CasbinAction, CasbinActions,
    UpdateCasbinActionInputDto
)

from adapter.schema.users import (AuthenticationInputDto)

from adapter.schema.users import UpdateUserRoleDto

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
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    The scopes parameter receives a dict with each scope as a key and the description as the value:

    """
    user = authenticate_user(form_data.username, form_data.password)
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

    enforce = e.enforce(current_user.username, "UserModel", "read")  # return judge result with reason
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
    enforce = e.enforce(current_user.username, "UserModel", "read")  # return judge result with reason
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
    enforce = e.enforce(current_user.username, "UserModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.change_user_status_reverse(user_id)

    return GeneralOutputDto()


@users_router.post("/user/delete_user",
                   description="删除用户",
                   response_model=GeneralOutputDto)
async def delete_single_user(request: Request,
                             current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                             executor: UsersExecutor,
                             e: Enforcer = Depends(get_casbin_e),
                             user_id: int = Field(default=0, gt=0, description="用户id，必须大于0")
                             ):
    enforce = e.enforce(current_user.username, "UserModel", "delete")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.delete_user_by_id(user_id)

    return GeneralOutputDto()


@users_router.post("/user/update_user",
                   description="更新user信息内容",
                   response_model=GeneralOutputDto)
async def update_user(request: Request,
                      current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                      executor: UsersExecutor,
                      e: Enforcer = Depends(get_casbin_e),
                      body: UpdateUserDto = Body(...)
                      ):
    """
    更新（旗下）用户信息
    处理别的用户信息，应该用id进行定位
    :param body:
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :return:
    """
    enforce = e.enforce(current_user.username, "UserModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    if executor.get_role_by_role_key(body.username):
        raise CredentialsException(detail="用户名称重复!", headers={"WWW-Authenticate": "Bearer"})

    await executor.update_user_baseInfo(
        user_id=body.user_id,
        username=body.username,
        fullname=body.fullname,
        email=body.email,
        avatar=body.avatar,
        remark=body.remark,
        password=body.password
    )

    return GeneralOutputDto(success=True)


@users_router.post("/user/update_me",
                   description="更新当前用户信息内容",
                   response_model=GeneralOutputDto)
async def update_me(request: Request,
                    current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                    executor: UsersExecutor,
                    e: Enforcer = Depends(get_casbin_e),
                    body: UpdateUserDto = Body(...)):
    """
    更改自己的信息，应该用 自己的 username 进行定位
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param body:
    :return:
    """
    enforce = e.enforce(current_user.username, "UserModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.update_user_baseInfo(
        user_id=current_user.user_id,
        username=body.username,
        fullname=body.fullname,
        email=body.email,
        avatar=body.avatar,
        remark=body.remark,
        password=body.password
    )

    return GeneralOutputDto(success=True)


@users_router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user_with_scope)]):
    return {"status": "ok"}


@users_router.post("/users/list",
                   description="获取用户列表",
                   response_model=UserListOutputDto
                   )
async def user_list(request: Request,
                    current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                    executor: UsersExecutor,
                    e: Enforcer = Depends(get_casbin_e),
                    body: UserListInputDto = Body(...)):
    enforce = e.enforce(current_user.username, "UserModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    all_users = await executor.all_users()

    return UserListOutputDto(data=all_users)


######################################
# Role相关的api接口
######################################

@users_router.get("/role/roles",
                  description="获取所有用户组",
                  response_model=Roles)
async def get_roles(request: Request,
                    current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                    executor: UsersExecutor,
                    e: Enforcer = Depends(get_casbin_e)):
    """
    获取所有的role
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :return:
    """
    enforce = e.enforce(current_user.username, "UserModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    roles = await executor.get_all_roles()
    data = []
    for role in roles:
        data.append(
            Role(
                role=role.role,
                role_key=role.role_key
            )
        )
    count = len(roles)

    return Roles(roles=data, count=count)


@users_router.post("/role/add",
                   description="添加角色", response_model=GeneralOutputDto)
@users_router.post("/role/create_role",
                   description="创建角色", response_model=GeneralOutputDto)
async def create_role(request: Request,
                      current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                      executor: UsersExecutor,
                      e: Enforcer = Depends(get_casbin_e),
                      body: CreateRoleInputDto = Body()):
    enforce = e.enforce(current_user.username, "RoleModel", "create")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.create_role(role_name=body.role,
                               role_key=body.role_key,
                               description=body.description,
                               created_by=current_user.user_id)

    return GeneralOutputDto(success=True)


@users_router.get("role/get",
                  description="根据角色id查看角色",
                  response_model=Role)
async def get_role_by_id(request: Request,
                         current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                         executor: UsersExecutor,
                         e: Enforcer = Depends(get_casbin_e),
                         role_id: int = Field(..., gt=0)):
    enforce = e.enforce(current_user.username, "RoleModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    role = await executor.get_role_by_id(role_id)

    return Role(role=role.role, role_key=role.role_key, description=role.description)


@users_router.post("/role/update",
                   description="更新角色信息",
                   response_model=GeneralOutputDto)
async def update_role(request: Request,
                      current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                      executor: UsersExecutor,
                      e: Enforcer = Depends(get_casbin_e),
                      body: UpdateRoleInputDto = Body(...)):
    """
     更新角色（用户组）信息，需要对应更新相关的casbin_rule关联用户组的role_key，更新相关的casbin_rule关联资源动作的role_key
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param body:
    :return:
    """

    enforce = e.enforce(current_user.username, "RoleModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.update_role_by_id(role_id=body.role_id, role_name=body.role, role_key=body.role_key)

    return GeneralOutputDto()


@users_router.post("/role/delete",
                   description="删除一个角色",
                   response_model=GeneralOutputDto)
async def delete_role_by_id(request: Request,
                            current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                            executor: UsersExecutor,
                            e: Enforcer = Depends(get_casbin_e),
                            role_id: int = Field(..., gt=0)):
    enforce = e.enforce(current_user.username, "RoleModel", "delete")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.delete_role_by_id(role_id)

    return GeneralOutputDto


@users_router.post("/user/change_user_role",
                   description="修改用户的所属角色（用户组）",
                   response_model=GeneralOutputDto)
async def change_users_role(request: Request,
                            current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                            executor: UsersExecutor,
                            e: Enforcer = Depends(get_casbin_e),
                            body: UpdateUserRoleDto = Body()
                            ):
    """
    修改用户所属角色或者用户组,复数，一个用户可以拥有多个角色
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param body:
    :return:
    """
    enforce = e.enforce(current_user.username, "UserModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.update_user_role(user_id=body.user_id, roles=body.roles)

    return GeneralOutputDto(success=True)


@users_router.get("/user/get_user_role",
                  description="获取用户所拥有的用户组",
                  response_model=UserRolesOutputDto)
async def get_user_role(request: Request,
                        current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                        executor: UsersExecutor,
                        e: Enforcer = Depends(get_casbin_e),
                        user_id: int = Field(gt=0, description="用户id，必须大于0")):
    """
      获取用户所拥有的用户组
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param user_id:
    :return:
    """
    enforce = e.enforce(current_user.username, "UserModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    user = await executor.get_user_by_id(user_id)
    # 获取所有的权限组
    all_roles = await executor.get_all_roles()
    options = [role.role for role in all_roles]

    # 获取该用户的所在用户组
    casbin_rules = await executor.get_casbin_rules_by_username(username=user.username)
    roles = [await executor.get_role_by_role_key(casbin_rule.v1) for casbin_rule in casbin_rules]

    checkeds = [role.role for role in roles]

    return UserRolesOutputDto(success=True,
                              data=UserRolesOutputData(options=options, checkeds=checkeds))


######################################
# casbin rule 规则权限相关的api接口
######################################

@users_router.get('/role/get_coca',
                  description="返回用户组role所包含的权限用于前端使用多选框来展示",
                  response_model=RoleCasbinOutputDto)
@users_router.get("/role/rules",
                  description="返回用户组role所包含的权限用于前端使用多选框来展示",
                  response_model=RoleCasbinOutputDto)
async def get_casbin_objects_rules(request: Request,
                                   current_user: Annotated[
                                       User, Security(get_current_active_user_with_scope, scopes=["me"])],
                                   executor: UsersExecutor,
                                   e: Enforcer = Depends(get_casbin_e),
                                   role_id: int = Field(gt=0, description="角色id，必须大于0")):
    """
    返回用户组role所包含的权限用于前端使用多选框来展示
    demo :
    <div  v-for="(item,index) of options.value" >
        <a-checkbox-group v-model:value="checkeds.value[index]" :options="item" />
    </div>

    其中options、checkeds是两个数组，前者包括了所有的权限列表，后者只包括当前用户组所拥有的权限。
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param role_id:
    :return:
    """
    enforce = e.enforce(current_user.username, "CasbinObjectModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})
    enforce = e.enforce(current_user.username, "CasbinActionModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})
    enforce = e.enforce(current_user.username, "CasbinRuleModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    role = await executor.get_role_by_id(primary_key=role_id)
    # 获取所有的 objects
    all_casbin_objects = await executor.get_all_casbin_objects()
    # 获取所有的 actions
    all_casbin_actions = await executor.get_all_casbin_actions()
    # 获取该角色的rules
    casbin_rules = await executor.get_casbin_rules_by_role_key(role.role_key)

    casbin_action_names = []
    cocas = []  # 拼装所有权限的列表
    casbin_object_key_name = {}  # 组装一个字典，里边的资源key对应name
    casbin_action_key_name = {}  # 组装一个字典，里边的动作key对应name
    cks = []
    checkeds = []  # 当前用户组所拥有的权限

    for casbin_action in all_casbin_actions:
        casbin_action_names.append(casbin_action.action_name)
        casbin_action_key_name[casbin_action.action_key] = casbin_action.action_name
    for casbin_object in all_casbin_objects:
        cocas.append([casbin_object.object_name] + casbin_action_names)
        casbin_object_key_name[casbin_object.object_key] = casbin_object.object_name

    for casbin_rule in casbin_rules:
        cks.append(casbin_object_key_name[casbin_rule.v1])
        cks.append(casbin_action_key_name[casbin_rule.v2])

    temp_names = list()
    for ck in cks:
        if len(temp_names) == 0:
            temp_names.append(ck)
        elif temp_names[0] == ck:
            pass
        elif ck in casbin_object_key_name.values() and ck != temp_names[0]:
            checkeds.append(temp_names)
            temp_names = [ck]
        elif ck in casbin_action_key_name.values() and ck not in temp_names:
            temp_names.append(ck)

    checkeds.append(temp_names)

    data = RoleCasbinOutputData(options=cocas, checkeds=checkeds)

    return RoleCasbinOutputDto(success=True, data=data)


@users_router.post("/role/change_role",
                   description="修改用户组所拥有的权限",
                   response_model=GeneralOutputDto)
@users_router.post("/role/change_cas",
                   description="修改用户组所拥有的权限",
                   response_model=GeneralOutputDto)
async def change_role_cas(request: Request,
                          current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                          executor: UsersExecutor,
                          e: Enforcer = Depends(get_casbin_e),
                          request_data: ChangeRoleCasbinRuleInputDto = Body(...)):
    enforce = e.enforce(current_user.username, "RoleModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    role = await executor.get_role_by_id(request_data.role_id)
    all_casbin_objects = await executor.get_all_casbin_objects()
    all_casbin_actions = await executor.get_all_casbin_actions()

    casbin_object_key_name = {}  # 组装一个字典，里边的资源key对应name
    casbin_action_key_name = {}  # 组装一个字典，里边的动作key对应name
    checkeds = request_data.checkeds
    rules = list()  # 整体收集更新规则

    for casbin_object in all_casbin_objects:
        casbin_object_key_name[casbin_object.object_name] = casbin_object.object_key
    for casbin_action in all_casbin_actions:
        casbin_action_key_name[casbin_action.action_name] = casbin_action.action_key

    for casbin_rules in checkeds:
        if casbin_rules:
            object_key = casbin_object_key_name[casbin_rules[0]]
            casbin_rule_name = casbin_rules[0]
            if len(casbin_rules) <= 1:
                return

            for casbin_rule in casbin_rules:
                if casbin_rule == casbin_rule_name:
                    rules.append([role.role_key, object_key, casbin_action_key_name[casbin_rule]])

    await executor.update_role_casbin_rules_ptype_p(role.role_key, casbin_rules=rules)

    return GeneralOutputDto(success=True)


######################################
# casbin object规则权限相关的api接口
######################################

@users_router.get("/co/cos",
                  description="获取所有的对象",
                  response_model=CasbinObjects)
async def get_casbin_objects(request: Request,
                             current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                             executor: UsersExecutor,
                             e: Enforcer = Depends(get_casbin_e)
                             ):
    enforce = e.enforce(current_user.username, "CasbinObjectModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    casbin_objects = await executor.get_all_casbin_objects()
    data = [CasbinObject(object_name=casbin_object.object_name, object_key=casbin_object.object_key,
                         description=casbin_object.description) for casbin_object in casbin_objects]

    count = len(casbin_objects)

    return CasbinObjects(count=count, casbin_objects=data)


@users_router.post("/co/create_co",
                   description="创建对象",
                   response_model=GeneralOutputDto)
async def create_casbin_object(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e),
                               request_data: CreateCasbinObjectInputDto = Body(...)):
    enforce = e.enforce(current_user.username, "CasbinObjectModel", "create")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})
    object_name = request_data.name
    object_key = request_data.object_key
    description = request_data.description

    await executor.add_casbin_object(object_name=object_name, object_key=object_key, description=description,
                                     created_by=current_user.user_id)


@users_router.get("/co/get_co",
                  description="获取单个操作对象",
                  response_model=CasbinObject)
async def get_casbin_object(request: Request,
                            current_user: Annotated[User, Security(get_current_active_user_with_scope, scopes=["me"])],
                            executor: UsersExecutor,
                            e: Enforcer = Depends(get_casbin_e),
                            co_id: int = Field(..., gt=0)):
    enforce = e.enforce(current_user.username, "CasbinObjectModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    casbin_object = await executor.get_casbin_object_by_id(co_id)

    return CasbinObject(object_name=casbin_object.object_name,
                        object_key=casbin_object.object_key,
                        description=casbin_object.description)


@users_router.post("/co/update_co",
                   description="更新对象信息",
                   response_model=GeneralOutputDto)
async def update_casbin_object(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e),
                               request_data: UpdateCasbinObjectInputDto = Body(...)):
    """
    更新object 信息
    :param request:
    :param current_user:
    :param executor:
    :param e:
    :param request_data:
    :return:
    """
    enforce = e.enforce(current_user.username, "CasbinObjectModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    co_id = request_data.co_id
    name = request_data.name
    object_key = request_data.object_key
    description = request_data.description
    await executor.update_casbin_object_by_id(co_id, name, object_key, description)

    return GeneralOutputDto()


@users_router.post('/co/delete_co',
                   response_model=GeneralOutputDto)
async def delete_casbin_object(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e),
                               co_id: int = Field(gt=0)):
    enforce = e.enforce(current_user.username, "CasbinObjectModel", "delete")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.delete_casbin_object_by_id(co_id)

    return GeneralOutputDto()


######################################
# Casbin Action 相关的api接口
######################################

@users_router.get("/ca/get_cas",
                  response_model=CasbinActions)
@users_router.get("/ca/cas",
                  response_model=CasbinActions)
async def get_casbin_actions(request: Request,
                             current_user: Annotated[
                                 User, Security(get_current_active_user_with_scope, scopes=["me"])],
                             executor: UsersExecutor,
                             e: Enforcer = Depends(get_casbin_e)):
    enforce = e.enforce(current_user.username, "CasbinActionModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    casbin_actions = await executor.get_all_casbin_actions()
    data = [CasbinAction(action_name=casbin_action.action_name, action_key=casbin_action.action_key,
                         description=casbin_action.description) for casbin_action in casbin_actions]

    count = len(casbin_actions)

    return CasbinActions(count=count, casbin_actions=data)


@users_router.post("/ca/create_ca",
                   response_model=GeneralOutputDto)
async def create_casbin_action(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e),
                               request_data: CreateCasbinActionInputDto = Body(...)):
    enforce = e.enforce(current_user.username, "CasbinActionModel", "create")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    action_name = request_data.name
    action_key = request_data.action_key
    description = request_data.description

    await executor.add_casbin_action(action_name, action_key, description, created_by=current_user.user_id)

    return GeneralOutputDto()


@users_router.get("/ca/get_ca",
                  response_model=CasbinAction)
async def get_ca(request: Request,
                 current_user: Annotated[
                     User, Security(get_current_active_user_with_scope, scopes=["me"])],
                 executor: UsersExecutor,
                 e: Enforcer = Depends(get_casbin_e),
                 ca_id: int = Field(gt=0)):
    enforce = e.enforce(current_user.username, "CasbinActionModel", "read")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    casbin_action = await executor.get_casbin_action_by_id(ca_id)

    return CasbinAction(action_name=casbin_action.action_name,
                        action_key=casbin_action.action_key,
                        description=casbin_action.description)


@users_router.post("/ca/update_ca",
                   response_model=GeneralOutputDto)
async def update_casbin_action(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e),
                               request_data: UpdateCasbinActionInputDto = Body(...)):
    enforce = e.enforce(current_user.username, "CasbinActionModel", "update")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    ca_id = request_data.ca_id
    action_name = request_data.name
    action_key = request_data.action_key
    description = request_data.description
    await executor.update_casbin_action_by_id(ca_id, action_name, action_key, description)

    return GeneralOutputDto


@users_router.post("/ca/delete_ca",
                   response_model=GeneralOutputDto)
async def delete_casbin_action(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e),
                               ca_id: int = Field(gt=0)):
    enforce = e.enforce(current_user.username, "CasbinActionModel", "delete")  # return judge result with reason
    if not enforce:
        raise CredentialsException(detail="您的账户权限不足!", headers={"WWW-Authenticate": "Bearer"})

    await executor.delete_casbin_action_by_id(ca_id)

    return GeneralOutputDto()


######################################
# Casbin 权限验证的api接口
######################################

@users_router.get("/get_menu")
async def get_menu_permissions(request: Request,
                               current_user: Annotated[
                                   User, Security(get_current_active_user_with_scope, scopes=["me"])],
                               executor: UsersExecutor,
                               e: Enforcer = Depends(get_casbin_e)):
    rules = [
        ['User', 'show'],
        ['Role', 'show'],
        ['CasbinObjectModel', 'show'],
        ['CasbinActionModel', 'show'],
    ]
    menu = {}
    for rule in rules:
        enforce = e.enforce(current_user.username, rule[0], rule[1])
        if enforce:
            menu[rule[0]] = True
        else:
            menu[rule[0]] = False
    return menu


@users_router.post("/isAuthenticated")
async def isAuthenticated(request: Request,
                          current_user: Annotated[
                              User, Security(get_current_active_user_with_scope, scopes=["me"])],
                          executor: UsersExecutor,
                          e: Enforcer = Depends(get_casbin_e),
                          request_data: AuthenticationInputDto = Body(...)):
    """
    路由页面的权限验证接口

    """
    return e.enforce(current_user.username, request_data.obj, request_data.action)


@users_router.post("casbin_rule_test")
async def casbin_test(request: Request,
                      current_user: Annotated[
                          User, Security(get_current_active_user_with_scope, scopes=["me"])],
                      executor: UsersExecutor,
                      e: Enforcer = Depends(get_casbin_e), ):
    return e.enforce(current_user.username, "User", "read")


if __name__ == '__main__':
    pass
