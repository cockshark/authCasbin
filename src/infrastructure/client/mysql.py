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

from peewee_async import PooledMySQLDatabase as AsyncPooledMySQLDatabase, Manager
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
        cls.pool = None # type :

        print(db_config)
        cls.get_db_instance(db_config, max_connections)
        super().__init_subclass__()

    @classmethod
    def get_db_instance(cls, db_config: dict, max_connections=10):
        if not cls.pool:  # inherit this
            cls.pool = cls(**db_config, max_connections=max_connections)

        return cls.pool


class RiskDbConn(ReconnectAsyncPooledMySQLDatabase, db_config=system_config.risk_mysql_cfg):
    """
    this has a cls attr :pool
    useage : RiskDbConn.pool  or self.pool
    """
    pass


if __name__ == '__main__':
    db = RiskDbConn.pool
    
    from peewee import (
        Model,
        BigIntegerField, SmallIntegerField,
        CharField,
        DateTimeField)
    
    class Service(Model):
        id = BigIntegerField(primary_key=True)
        group_id = SmallIntegerField(null=False)
        env_id = SmallIntegerField(null=True, help_text="默认执行环境")
        service = CharField(max_length=64, help_text="jenkins上对应的服务名")
        prefix = CharField(max_length=128, default="", help_text="服务前缀名")
        work_id = SmallIntegerField(help_text="所属项目")
        create_date = DateTimeField(formats=DateTimeField.formats[1])

        class Meta:
            database = db
            table_name = "t_service"

    objects = Manager(db)
    db.set_allow_sync(True)

    # FIX THE YAML database : testdb
    sync_query_list = Service.select(Service.id, Service.create_date).where(Service.id >= 1).execute()

    assert len(sync_query_list)
