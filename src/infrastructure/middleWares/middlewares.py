#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   middlewares.py
@Time    :   2023/3/23 11:31
@Desc    :


SessionMiddleware :
    使用后端存储来持久化客户端状态（即使用Cookies）。
    它通过生成一个UUID来完成会话的唯一性，并将其保存到客户端的cookie中。
    在每个请求中，会话中间件会读取cookie值，并将其映射到会话存储的值。

CorrelationIdMiddleware
    为每个请求增加唯一的id，注入到日志，方便查看请求

'''

__author__ = "wush"

from asgi_correlation_id import CorrelationIdMiddleware

from .timerMiddleware import TimerMiddleware

MIDDLEWARES = [
    CorrelationIdMiddleware,
    TimerMiddleware
]
