#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   defaultFileAdater.py
@Time    :   2023/3/12 16:21
@Desc    :

'''

__author__ = "wush"

import casbin
import casbin_sqlalchemy_adapter

from conf import (RBAC_MODEL_CONF, RBAC_POLICY_CONF)

# Use the Model file and default FileAdapter:
e = casbin.Enforcer(RBAC_MODEL_CONF, RBAC_POLICY_CONF)

sub = "alice"  # the user that wants to access a resource.
obj = "data1"  # the resource that is going to be accessed.
act = "read"  # the operation that the user performs on the resource.

if e.enforce(sub, obj, act):
    # permit alice to read data1
    pass
else:
    # deny the request, show an error
    pass


roles = e.get_roles_for_user("alice")


if __name__ == '__main__':
    print(roles)
