#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   error.py
@Time    :   2023/3/22 18:04
@Desc    :

'''

__author__ = "wush"

from typing import Optional

from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    message: Optional[str] = Field(description="错误信息")
    err_code: str = Field(description="错误码")
    err_msg: Optional[str] = Field(description="定义的错误信息", default="")
    extra: dict = Field(description="extra错误信息", default="")


