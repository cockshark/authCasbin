#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   SQLLiteAdapter.py
@Time    :   2023/3/12 17:13
@Desc    :

'''

__author__ = "wush"

import casbin
import casbin_sqlalchemy_adapter

from conf import RBAC_MODEL_CONF

# Use the Model text with other Adapter:
# Use SQLAlchemy Casbin adapter with SQLLite DB
adapter = casbin_sqlalchemy_adapter.Adapter('sqlite:///test.db')

# Create a config model policy,
# with open("rbac_example_model.conf", "w") as f:
#     f.write("""
#     [request_definition]
#     r = sub, obj, act
#
#     [policy_definition]
#     p = sub, obj, act
#
#     [policy_effect]
#     e = some(where (p.eft == allow))
#
#     [matchers]
#     m = r.sub == p.sub && r.obj == p.obj && r.act == p.act
#     """)

# Create enforcer from adapter and config policy
e = casbin.Enforcer(RBAC_MODEL_CONF, adapter)

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
