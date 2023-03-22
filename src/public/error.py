#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :
@Software:   PyCharm
@File    :   error.py
@Time    :   2023/3/22 18:00
@Desc    :

'''

__author__ = "wush"

from fastapi import Request

from adapter.schema.error import ErrorInfo


def request_error_info(e: Exception, request: Request):
    """
    整理报错信息
    :param e:
    :param request:
    :return:
    """
    message = ""  # type:str
    err_code = ""  # type:str
    err_msg = ""  # type:str
    extra: dict = {
        # "error_code": "",
        # "error_msg": "",
        # ...  其他字段
    }

    return ErrorInfo(
        message=message,
        err_code=err_code,
        err_msg=err_msg,
        extra=extra
    )


if __name__ == '__main__':
    pass
