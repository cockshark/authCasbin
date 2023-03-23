#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   authCasApp.py
@Time    :   2023/3/16 14:36
@Desc    :

'''

__author__ = "wush"

import argparse

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from adapter.router import router as apiRouter
from infrastructure.config.config import system_config
from infrastructure.log.log import logger
from infrastructure.middleWares.middlewares import MIDDLEWARES


def create_fastAPI_application() -> FastAPI:
    from settings import settings

    authCasbin = FastAPI(**settings)
    authCasbin.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for middleware in MIDDLEWARES:
        authCasbin.add_middleware(middleware)

    authCasbin.include_router(apiRouter)

    return authCasbin


if __name__ == '__main__':
    """
        deployment port : 8788
    """
    # python3 src/authCasApp.py --host=0.0.0.0 --port=8788 --workers 4
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str)
    parser.add_argument('--port', type=int)
    args = parser.parse_args()

    authCasbinApp = create_fastAPI_application()

    # uvicorn.run(authCasbinApp, host=args.host, port=args.port, loop="auto")

    uvicorn.run(authCasbinApp, host="0.0.0.0", port=8788)
    logger.info(f"authCasbin running port {system_config.port}")
