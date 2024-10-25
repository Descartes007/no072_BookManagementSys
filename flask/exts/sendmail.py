#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
@Time    : 2024年02月19日14:16分
@Author  : anonymous
@Description:  发送邮件通知
'''

import smtplib

from flask import request

import settings
from email.mime.text import MIMEText

# from exts.logHandler import base_logger,audit_logger
from exts.logHandler import base_logger as logger
from exts.logHandler import audit_logger
def send_mail(sender, reciver, title, msg_content):
    msg = MIMEText(msg_content)
    # 加邮件头
    msg['to'] = reciver
    msg['from'] = sender
    # 邮件主题
    msg['subject'] = title
    # 发送邮件
    server = smtplib.SMTP()
    server.set_debuglevel(settings.Config.EMAIL_DEBUG_LEVEL)
    server.connect(settings.Config.EMAIL_SERVER_ADDR, settings.Config.EMAIL_SERVER_PORT)

    try:
        server.login(settings.Config.EMAIL_USERNAME, settings.Config.EMAIL_PASSWORD)
        server.sendmail(msg['from'], msg['to'], msg.as_string())
        logger.debug("send mail to " + reciver + " success")
        audit_logger.debug("[{0}] [{1}] [密码找回] [向{2}发送了邮件]".format(request.remote_addr, '系统',reciver))
    except Exception as e:
        print(e)
        logger.error("send mail to " + reciver + " fail")
        return False
    else:
        server.quit()
        return True
