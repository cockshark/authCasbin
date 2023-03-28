#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   fastapiBaseRouter.py
@Time    :   2023/3/16 14:53
@Desc    :

'''

__author__ = "wush"

import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute, Callable, Request

from adapter.schema.baseResponse import ResponseModel
from infrastructure.log.log import logger
from public.error import request_error_info


class CustomRSPRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start = time.time()
            try:
                logger.info(f"body: {await request.body()}, "
                            f"headers: {request.headers}, "
                            f"url: {request.url}")
                rsp = await original_route_handler(request)
                return rsp
            except Exception as e:
                error_info = request_error_info(e, request)
                logger.error(error_info.message, extra=error_info.extra, exc_info=True)
                return JSONResponse(
                    ResponseModel(
                        success=False,
                        err_code=error_info.err_code,
                        err_msg=error_info.err_msg
                    ).dict(by_alias=self.response_model_by_alias)
                )
            finally:
                elapsed = round(time.time() - start, 2)
                logger.info(
                    f"request_elapsed",
                    extra={"url": str(request.base_url),
                           "elapsed": {elapsed}}
                )

        return custom_route_handler


class BaseAPIRouter(APIRouter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.route_class = CustomRSPRoute
        self.default_response_class = JSONResponse
