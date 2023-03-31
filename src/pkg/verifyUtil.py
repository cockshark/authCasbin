#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   verifyUtil.py
@Time    :   2023/3/31 17:54
@Desc    :

'''

__author__ = "wush"

from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from adapter.schema.users import UserInDB

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",
                                     scopes={"me": "Read information about the current user.", "items": "Read items."},)


def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


def get_user(users: Dict[str, Dict], username: str) -> Optional[UserInDB]:
    if username in users:
        user_dict = users[username]
        return UserInDB(**user_dict)


def generate_access_token(data: dict, secret_key: str, algorithm: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def get_password_hash(password):
    return password_context.hash(password)


if __name__ == '__main__':
    pass
