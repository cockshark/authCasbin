#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   config.py
@Time    :   2023/3/16 13:23
@Desc    :
配置定义及其解析
'''

__author__ = "wush"

import argparse
from pathlib import Path
from typing import Optional

from pkg.functional import SimpleLazyObject


class Config:
    log_root: Optional[Path] = None  # common : $project_path/logs

    def __init__(self):
        self.port: Optional[int] = None
        self.task_name: Optional[str] = None

        # init
        self.parser = None  # type: Optional[argparse.ArgumentParser]
        self.init_options()
        self.logPath()

    def init_options(self):
        """启动时候可指定命令行环境，也可以直接传入 (跑脚本的场景)"""
        self.parser = parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument(
            "--port",
            default="8788",
            help="定义服务主程序启动端口，默认8788",
            type=int
        )

        parser.add_argument(
            "--task_name",
            default="placeholder",
            help=f"用于定时任务的task name",
            type=str
        )

        args, unknown = parser.parse_known_args()
        self.port = args.port

    @classmethod
    def logPath(cls) -> None:
        project = Path(__file__).parent.parent.parent.parent

        cls.log_root = project.joinpath("logs")

        if not cls.log_root.exists():
            cls.log_root.mkdir(parents=True)

    def __str__(self):
        msg = self.__class__.__name__ + "\n"
        for attr, value in self.__dict__.items():
            msg += f" ({attr}: {value}) \n"
        return msg


system_config = SimpleLazyObject(Config)


if __name__ == '__main__':
    ob = Config()
