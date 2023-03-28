#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 20:42
@Desc    :

'''

__author__ = "wush"

from typing import Optional, List

from application.dto.users import CommonUser
from domain.gateway.users import CommonUserManager


class Users:

    def __init__(self, user_manager: CommonUserManager = CommonUserManager()):
        self.user_manager = user_manager

    async def all_users(self) -> Optional[List[CommonUser]]:
        """
           数据量大可以改成流式查询接口， 使用 pymysql.cursors.SSCursor
        :return:
        """
        self.user_manager.all_users()


if __name__ == '__main__':
    pass
