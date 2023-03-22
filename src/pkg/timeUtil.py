#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   timeUtil.py
@Time    :   2023/3/16 14:58
@Desc    :

'''

__author__ = "wush"

import time

import arrow


def now(fmt="YYYY-MM-DD HH:mm:ss ", **kwargs):
    days = kwargs.get("days", 0)
    hours = kwargs.get("hours", 8)
    local = arrow.utcnow().shift(days=days, hours=hours)
    if fmt:
        return local.format(fmt)
    return local.datetime


def currentTimeMillisecond() -> int:
    return int(time.time() * 1000)


if __name__ == '__main__':
    print(now(fmt=None))
    print(now())
