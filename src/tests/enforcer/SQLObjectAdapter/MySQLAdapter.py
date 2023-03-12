#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   MySQLAdapter.py
@Time    :   2023/3/12 17:14
@Desc    :

'''

__author__ = "wush"

import casbin
import casbin_sqlobject_adapter

from conf import RBAC_MODEL_CONF

adapter = casbin_sqlobject_adapter.Adapter("mysql://scott:tiger@localhost/foo")
e = casbin.Enforcer(RBAC_MODEL_CONF, adapter)

if __name__ == '__main__':
    pass
