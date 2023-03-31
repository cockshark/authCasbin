#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   users.py
@Time    :   2023/3/23 20:57
@Desc    :

'''

__author__ = "wush"

from typing import Optional, List

from domain.model.users import UserModel


class CommonUserManager:
    async def all_users(self) -> Optional[List[UserModel]]:
        """

        要处理掉不需要的字段信息
        :return:
        """
        pass


if __name__ == '__main__':
    pass
