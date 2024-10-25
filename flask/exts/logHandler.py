#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
@Time    : 2023年06月17日16:43分
@Author  : Anonymous
@Description: 
'''
import logging
import sys

import loguru

sys.path.append("..")
from logging.handlers import RotatingFileHandler
import settings
from loguru import logger as LOGGER

# def base_log_handler(modelName, logFileName,logLevel='DEBUG'):
#     # 创建日志对象，设置默认日志等级
#     logger = logging.getLogger(modelName)
#     logger.setLevel(logging.DEBUG)
#     # 日志输出格式
#     formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(filename)s] - [line:%(lineno)s] - [%(levelname)s] - %(message)s')

#     # 创建控制台日志处理器
#     console_handler = logging.StreamHandler()
#     # 控制台日志处理器日志等级和日志格式
#     console_handler.setLevel(logging.DEBUG)
#     console_handler.setFormatter(formatter)
#     # 将控制台日志处理器加入日志处理器对象
#     logger.addHandler(console_handler)

#     # 创建日志文件处理器
#     file_handler = RotatingFileHandler(logFileName,'a',encoding='utf-8',maxBytes=1024 * 1024 * 100, backupCount=10)
#     file_handler.setLevel(logging.DEBUG)
#     file_handler.setFormatter(formatter)
#     # 将日志文件器添加进日志器对象
#     logger.addHandler(file_handler)
#     return logger


# def base_log_handler(logFileName='run.log'):
#     log_dir = settings.Config.LOG_BASE_DIR
#     log_level = 'DEBUG'
#     log_size_max = "10 MB"
#     log_file_num = 5
#
#     LOGGER.add(log_dir + logFileName, level=log_level,
#                format="[{time:%Y-%m-%d %H:%M:%S}] | {level} | {file}:{function}:{line} |{message}",
#                rotation=log_size_max, retention=int(log_file_num),
#                filter=lambda record: record["extra"].get("name") == "base")
#
#     LOGGER.add(log_dir + "audit.log", level="DEBUG",
#                format="[{time:%Y-%m-%d %H:%M:%S}] | {message}",
#                rotation='100 MB', retention=5, filter=lambda record: record["extra"].get("name") == "audit")
#
#     logger_base = LOGGER.bind(name='base')
#     logger_audit = LOGGER.bind(name='audit')
#     return logger_base, logger_audit

from loguru import logger


# class CustomLogger:
#     log_dir = settings.Config.LOG_BASE_DIR
#     log_level = 'DEBUG'
#     log_size_max = "10 MB"
#     log_file_num = 5
#
#     def __init__(self, name='run.log'):
#         self.logFileName = name
#
#     #     self._logger.add(
#     #         sink=log_filename,
#     #         level=level,
#     #         format=log_format,
#     #         rotation=rotation,
#     #         retention=retention,
#     #     )
#     def base_log_handler(self):
#         LOGGER.add(self.log_dir + self.logFileName, level=self.log_level,
#                    format="[{time:%Y-%m-%d %H:%M:%S}] | {level} | {file}:{function}:{line} |{message}",
#                    rotation=self.log_size_max, retention=int(self.log_file_num))
#         return LOGGER
#     # 创建两个自定义 logger 实例
#
#     def audit_log_handler(self):
#         LOGGER.add(settings.Config.LOG_BASE_DIR + "audit.log",
#                    format="[{time:%Y-%m-%d %H:%M:%S}] | {message}",
#                    rotation="100 MB",
#                    retention=5,
#                    level="DEBUG",
#                    )
#         return LOGGER

# 创建两个独立的logger实例
# 创建一个全局的 logger
from loguru import logger
# 定义基础日志处理器
logger.add(
    sink=settings.Config.LOG_BASE_DIR + "{time:%Y-%m-%d-%H-%M-%S}"+"-run.log",
    level="DEBUG",
    format="[{time:%Y-%m-%d %H:%M:%S}] | {level} | {file}:{function}:{line} | {message}",
    rotation="200 MB",
    retention=5,
    filter=lambda record: record["extra"].get("type") == "base",
)
# 定义审计日志处理器
# logger.add(
#     sink=settings.Config.LOG_BASE_DIR + "audit.log",
#     level="DEBUG",
#     format="[{time:%Y-%m-%d %H:%M:%S}] | {message}",
#     rotation="100 MB",
#     retention=10,
#     filter=lambda record: record["extra"].get("type") == "audit",
# )


# 为方便在其他模块中使用，提供带上下文的记录方法
base_logger=logger.bind(type='base')
audit_logger=logger.bind(type='audit')
# 导出logger供其他模块使用
__all__ = ["base_logger", "audit_logger"]
