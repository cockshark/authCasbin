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

from fastapi import Request, HTTPException, status

from application.dto.error import ErrorInfo

# 错误级别
CLIENT_ERR_LEVEL_CODE = "4"
INNER_ERR_LEVEL_CODE = "5"
EXTERNAL_ERR_LEVEL_CODE = "6"

# 错误类型
INNER_ERR_TYPE_CODE = "00"
PARAM_ERR_TYPE_CODE = "01"

PARAM_ERROR_CODE = f"{CLIENT_ERR_LEVEL_CODE}{PARAM_ERR_TYPE_CODE}01"  # 参数缺失/格式错误
INNER_ERROR_CODE = f"{INNER_ERR_LEVEL_CODE}{INNER_ERR_TYPE_CODE}00"  # 服务内部异常
INNER_ERROR_MSG = f"Inner error."


def request_error_info(e: Exception, request: Request):
    """
    整理报错信息
    :param e:
    :param request:
    :return:
    """
    if isinstance(e, RoleNotExistError):
        message = e.error_msg
        err_msg = e.error_msg
        err_code = e.error_code
        extra = {
            "error_headers": str(request.headers),
            "error_msg": message,
            "url": str(request.url)
        }
    if isinstance(e, CredentialsException):
        message = "用户名不能跟角色key重复"
        err_msg = e.detail
        err_code = e.status_code
        extra = {
            "error_headers": str(request.headers),
            "error_msg": message,
            "url": str(request.url)
        }
    else:
        message = (
            f"inner error,"
            f"error: {format(e)}, "
            f"url: {request.url}, "
            f"headers: {request.headers}, "
            f"body: {request._body}"
        )
        err_code, err_msg = INNER_ERROR_CODE, INNER_ERROR_MSG
        extra = {"url": str(request.url)}

    return ErrorInfo(
        message=message,
        err_code=err_code,
        err_msg=err_msg,
        extra=extra
    )


class RoleNotExistError(Exception):
    error_code = PARAM_ERROR_CODE

    def __init__(self, *, role_key: str):
        self.error_msg = f"query role_key '{role_key}' not exits"


class CredentialsException(HTTPException):

    def __init__(self,
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail="用户名称重复！",
                 headers=None):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code, detail, headers)


if __name__ == '__main__':
    pass
