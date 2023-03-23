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
from typing import Callable

import arrow
from pydantic import Field


def now(fmt="YYYY-MM-DD HH:mm:ss ", **kwargs):
    days = kwargs.get("days", 0)
    hours = kwargs.get("hours", 8)
    local = arrow.utcnow().shift(days=days, hours=hours)
    if fmt:
        return local.format(fmt)
    return local.datetime


def currentTimeMillisecond() -> int:
    return int(time.time() * 1000)


class Timer:
    generator: int = Field(default_factory=currentTimeMillisecond)
    generator_1: int = Field(default=currentTimeMillisecond())

