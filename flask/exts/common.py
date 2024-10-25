#!/usr/bin/env python3
# ! -*- coding=utf-8 -*-
'''
**************************************************************
** 创建日期：2023/6/19 12:31
** 版    权：anonymous
** 功    能：
** 备    注：
**************************************************************
'''
import random

from apps.audit.model import Audit
from exts import db
from exts.logHandler import base_logger as logger


def generate_random_str(randomlength=16):
    '''
    生成指定长度的随机字符串
    :param randomlength:字符串长度,默认16个字节
    :return:
    '''
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz1234567890'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def insert_audit_log(ip, user, module, event):
    try:
        col = Audit(op_ip=ip, op_user=user, op_module=module, op_event=event)
        db.session.add(col)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("commit audit info fail")
        logger.exception(e)
