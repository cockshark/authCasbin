#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   settings.py
@Time    :   2023/3/23 11:34
@Desc    :


'''

__author__ = "wush"

import asyncio


async def startup():
    await asyncio.sleep(0.00001)


async def shutdown():
    await asyncio.sleep(0.00001)


settings = {
    "title": "fastAPI·用户后台管理系统",
    "description": "用户管理api",
    "version": "0.0.2",
    "on_startup": [startup],
    "on_shutdown": [shutdown],
}
