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

from application.executor.users import UsersExecutor
from infrastructure.log.log import logger


async def startup():
    logger.info("start service")
    await UsersExecutor().create_start_data()
    await asyncio.sleep(0.00001)


async def shutdown():
    logger.info("shutdown service")
    await asyncio.sleep(0.00001)


DEBUG = True

settings = {
    "debug": DEBUG,
    "title": "fastAPI·用户后台管理系统",
    "description": "用户管理api",
    "version": "0.0.3",
    "on_startup": [startup],
    "on_shutdown": [shutdown],
}
