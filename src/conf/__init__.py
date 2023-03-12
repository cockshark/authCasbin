#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   __init__.py
@Time    :   2023/3/12 16:29
@Desc    :

'''

__author__ = "wush"

from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.parent  # project path
SOURCE_ROOT = PROJECT_PATH.joinpath("src")  # src/
CONF_PKG_PATH = SOURCE_ROOT.joinpath("conf")  # conf/

# conf file path

RBAC_MODEL_CONF = CONF_PKG_PATH.joinpath("rbac_model.conf")
RBAC_POLICY_CONF = CONF_PKG_PATH.joinpath("rbac_policy.conf")

if __name__ == '__main__':
    print(PROJECT_PATH)
    print(SOURCE_ROOT)
    print(CONF_PKG_PATH)
    print(RBAC_MODEL_CONF)
    print(RBAC_POLICY_CONF)
