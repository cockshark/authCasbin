#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   timerMiddleware.py
@Time    :   2023/3/23 14:11
@Desc    :

Record the response time and put it in the request header.
and insert X-request-time：200ms

key:X-request-time
value: str
value type: str
'''

__author__ = "wush"

import typing
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from pkg.timeUtil import currentTimeMillisecond

RequestResponseEndpoint = typing.Callable[[Request], typing.Awaitable[Response]]
DispatchFunction = typing.Callable[
    [Request, RequestResponseEndpoint], typing.Awaitable[Response]
]


class TimerMiddleware(BaseHTTPMiddleware):
    header_name: str = 'X-Request-Time'

    def __init__(self, app: ASGIApp, dispatch: typing.Optional[DispatchFunction] = None) -> None:
        self.app = app
        # timer-generating callable
        self.generator: Callable[[], int] = currentTimeMillisecond
        super().__init__(app, dispatch=dispatch)

    # dispatch 必须实现
    async def dispatch(self, request, call_next: RequestResponseEndpoint) -> None:
        # Generate request time
        start_value = self.generator()

        response = await call_next(request)

        # update request time
        response.headers[self.header_name] = f"{currentTimeMillisecond() - start_value} ms"

        return response
