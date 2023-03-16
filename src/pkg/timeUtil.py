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


def currentTimeMillisecond() -> int:
    return int(time.time() * 1000)


if __name__ == '__main__':
    pass
