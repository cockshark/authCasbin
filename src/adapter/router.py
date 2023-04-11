#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   router.py
@Time    :   2023/3/16 14:15
@Desc    :

'''

__author__ = "wush"

from fastapi import APIRouter, Response

router = APIRouter()


@router.get('/')
def index(response: Response):
    return {"msg": "hello"}


if __name__ == '__main__':
    pass
