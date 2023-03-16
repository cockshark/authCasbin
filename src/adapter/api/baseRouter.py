#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   baseRouter.py
@Time    :   2023/3/16 14:53
@Desc    :

'''

__author__ = "wush"

import time
import logging
from fastapi import APIRouter
from fastapi.routing import APIRoute, Callable, Request
from fastapi.responses import JSONResponse, Response

from public.error import get_request_error_info
from adapter.schema.baseResponse import ResponseModel


class CustomRSPRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start = time.time()
            try:
                logging.info(f"body: {await request.body()}, "
                             f"headers: {request.headers}, "
                             f"url: {request.url}")
                rsp = await original_route_handler(request)
                return rsp
            except Exception as e:
                error_info = get_request_error_info(e, request)
                logging.error(error_info.message, extra=error_info.extra, exc_info=True)
                return JSONResponse(
                    ResponseModel(
                        success=False,
                        err_code=error_info.err_code,
                        err_msg=error_info.err_msg
                    ).dict(by_alias=self.response_model_by_alias)
                )
            finally:
                elapsed = round(time.time() - start, 2)
                logging.info(
                    f"request_elapsed",
                    extra={"url": str(request.base_url),
                           "elapsed": {elapsed}}
                )

        return custom_route_handler


class BaseAPIRouter(APIRouter):
    def __init__(self) -> None:
        super().__init__()
        self.route_class = CustomRSPRoute
        self.default_response_class = JSONResponse


if __name__ == '__main__':
    pass
