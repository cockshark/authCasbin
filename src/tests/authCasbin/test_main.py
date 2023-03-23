#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   test_main.py
@Time    :   2023/3/23 17:58
@Desc    :

'''

__author__ = "wush"

import requests


def test_hello_world():
    response = requests.get("http://localhost:8788/")

    request_time = response.headers["x-request-time"]
    assert request_time.endswith("ms")

