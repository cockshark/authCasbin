#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   baseResponse.py
@Time    :   2023/3/16 14:56
@Desc    :

'''

__author__ = "wush"

from typing import Optional

from pydantic import BaseModel, Field

from pkg.timeUtil import currentTimeMillisecond


class ResponseModel(BaseModel):
    success: bool = Field(default=True, description="服务状态 true-服务处理请求正常 false-服务处理请求失败")
    sys_time: int = Field(description="服务器时间", default=currentTimeMillisecond())
    errCode: Optional[str] = Field(description="success为false时的错误码", default="", alias="err_code")
    errMsg: Optional[str] = Field(description="success为false时的错误信息", default="", alias="err_msg")


if __name__ == '__main__':
    pass
