#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/31 17:37
@Desc    :

'''

__author__ = "wush"

from datetime import timedelta
from typing import Optional, Annotated, Dict

from authlib.jose import jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import SecurityScopes
from jose import JWTError
from pydantic import ValidationError

from adapter.schema.users import AppTokenConfig, TokenData, User
from application.executor.users import UsersExecutor
from infrastructure.log.log import logger
from pkg.verifyUtil import (
    get_user,
    verify_password,
    generate_access_token, oauth2_scheme
)


def authenticate_user(users, username: str, password: str):
    user = get_user(users, username)
    if not user:
        logger.error(f"user {username} not exist")
        return False
    if not verify_password(password, user.hashed_password):
        logger.error("password not correct")
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return generate_access_token(data, AppTokenConfig.SECRET_KEY, AppTokenConfig.ALGORITHM, expires_delta=expires_delta)


async def get_users_from_db() -> Optional[Dict[str, dict]]:
    executor = UsersExecutor()
    return await executor.name_all_users()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, AppTokenConfig.SECRET_KEY, algorithms=[AppTokenConfig.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error(f"user : {username} not exist")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    usersInDb = await get_users_from_db()
    user = get_user(usersInDb, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_with_scope(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, AppTokenConfig.SECRET_KEY, algorithms=[AppTokenConfig.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])  # get scopes
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    usersInDb = await get_users_from_db()
    user = get_user(usersInDb, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user_with_scope(
        current_user: Annotated[User, Security(get_current_user_with_scope, scopes=["me"])]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


if __name__ == '__main__':
    pass
