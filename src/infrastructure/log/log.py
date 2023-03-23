#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   wush
@License :   (C) Copyright 2021-9999, {AKULAKU}
@Contact :   
@Software:   PyCharm
@File    :   log.py
@Time    :   2023/3/16 13:26
@Desc    :
日志封装
'''

__author__ = "wush"

from pathlib import Path

from asgi_correlation_id import correlation_id

from infrastructure.config.config import system_config
from pkg.functional import SimpleLazyObject
from pkg.timeUtil import now

LOGGING_FORMATTER = "{extra[utc]}|{level}|requestId:{correlation_id}|{file}|func:{function}|{line}|{message}"


class LoggerFactory:
    root_log: Path
    error_log: Path

    @staticmethod
    def correlation_id_filter(record):
        record['correlation_id'] = correlation_id.get()
        return record['correlation_id']

    @classmethod
    def configure(cls):
        log_root = system_config.log_root  # type: Path
        if system_config.task_name:
            log_root = log_root.joinpath(system_config.task_name)

        print(f"log path root :{log_root}")

        cls.root_log = log_root.joinpath("root.log")
        cls.error_log = log_root.joinpath("error.log")

        print(cls.root_log, cls.error_log)

    @classmethod
    def create_logger(cls):
        from loguru import logger


        cls.configure()
        # info debug .etc
        logger.add(cls.root_log,
                   format=LOGGING_FORMATTER,
                   level="INFO",
                   filter=cls.correlation_id_filter,
                   rotation="512 MB",
                   retention="10 days",
                   colorize=True,
                   backtrace=True,
                   enqueue=True,  # 多進程安全
                   diagnose=True)  # # diagnose,backtrace 追踪显示整个堆栈跟踪，包括变量的值

        # error
        logger.add(cls.error_log,
                   format=LOGGING_FORMATTER,
                   level="ERROR",
                   filter=cls.correlation_id_filter,
                   rotation="512 MB",
                   retention="10 days",
                   colorize=True,
                   backtrace=True,
                   enqueue=True,  # 多進程安全
                   diagnose=True)  # # diagnose,backtrace 追踪显示整个堆栈跟踪，包括变量的值

        logger.patch(lambda record: record['extra'].update(utc=now()))

        return logger


"""
Making logger globally available, but to make it configurable logger lazy-evaluated.
"""
logger = SimpleLazyObject(LoggerFactory.create_logger)

if __name__ == '__main__':
    LoggerFactory.configure()
    logger.info("iiiiiiiii")
    logger.debug("deubg")
    logger.error("exexexexe")
