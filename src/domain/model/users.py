#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 21:03
@Desc    :

'''

__author__ = "wush"

from peewee import Model


class CommonUserModel(Model):
    class Meta:
        table_name = "user"


if __name__ == '__main__':
    pass
