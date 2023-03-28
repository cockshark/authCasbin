#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   mysql.py
@Time    :   2023/3/16 13:21
@Desc    :
构建 MySQL client  基于peewee目前
'''

__author__ = "wush"

from peewee_async import PooledMySQLDatabase as AsyncPooledMySQLDatabase

from playhouse.shortcuts import ReconnectMixin

from infrastructure.config.config import system_config

__all__ = ['RiskDbConn']


class ReconnectAsyncPooledMySQLDatabase(ReconnectMixin, AsyncPooledMySQLDatabase):
    pool = None

    def __init_subclass__(cls, db_config: dict, max_connections: int = 10):
        """
        定义衍生类，会自动给属性 pool
            param db_config : 配置
            max_connections ： 最大链接数
        """
        # init some class attr
        cls.pool = None

        db_config = cls.__adapter_db_cfg(db_config)
        cls.get_db_instance(db_config, max_connections)
        super().__init_subclass__()

    @classmethod
    def __adapter_db_cfg(cls, db_config: dict) -> dict:
        db_config["database"] = db_config["db"]
        db_config.pop("db")

        return db_config

    @classmethod
    def get_db_instance(cls, db_config: dict, max_connections=10):
        if not cls.pool:  # inherit this
            cls.pool = cls(**db_config, max_connections=max_connections)

        return cls.pool


class RiskDbConn(ReconnectAsyncPooledMySQLDatabase, db_config=system_config.mysql_user_config()):
    """
    this has a cls attr :pool
    useage : RiskDbConn.pool  or self.pool
    """
    pass

