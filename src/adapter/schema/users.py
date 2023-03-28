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

from pydantic import BaseModel

from adapter.schema.baseResponse import ResponseModel


class UserListInputDto(BaseModel):
    pass


class UserListOutputData(BaseModel):
    """
        todo: 展示用户的关键字段信息
    """
    pass


class UserListOutputDto(ResponseModel):
    data: Optional[List[UserListOutputData]]


if __name__ == '__main__':
    pass
