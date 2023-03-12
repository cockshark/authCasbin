#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   peeweeAdapter.py
@Time    :   2023/3/12 18:30
@Desc    :

'''

__author__ = "wush"

import casbin_peewee_adapter
import casbin
import peewee

from conf import RBAC_MODEL_CONF

DATABAEE = peewee.SqliteDatabase('db.sqlite3')
adapter = casbin_peewee_adapter.Adapter(database=DATABAEE)

e = casbin.Enforcer(RBAC_MODEL_CONF, adapter)

sub = "alice"  # the user that wants to access a resource.
obj = "data1"  # the resource that is going to be accessed.
act = "read"  # the operation that the user performs on the resource.

if e.enforce(sub, obj, act):
    # permit alice to read data1casbin_peewee_adapter
    pass
else:
    # deny the request, show an error
    pass

if __name__ == '__main__':
    pass
