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
    role_key: str


if __name__ == '__main__':
    pass
