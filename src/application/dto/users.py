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

from pydantic import BaseModel


class CommonUser(BaseModel):
    """
    对应数据库的关键字段
    """
    pass


if __name__ == '__main__':
    pass
