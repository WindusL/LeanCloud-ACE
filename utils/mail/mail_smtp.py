#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import os
import logging
import smtplib
from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText

logging.basicConfig(level=logging.DEBUG)


class MailSMTP(object):
    __site_name = os.environ['SITE_NAME']
    __smtp_user = os.environ['SMTP_USER']
    __smtp_pass = os.environ['SMTP_PASS']
    __smtp_host = os.environ['SMTP_HOST']
    __smtp_port = os.environ['SMTP_PORT']
    __sender_name = os.environ['SENDER_NAME']

    def __init__(self, to_addr):
        self.__to_addr = to_addr

    # 发送邮件
    def send_mail(self, msg):
        logging.debug(msg)
        # 封装消息
        message = MIMEText(msg, 'html', 'utf-8')
        message['From'] = formataddr(['%s' % self.__site_name, '%s' % self.__smtp_user])
        message['To'] = formataddr(['我', '%s' % self.__to_addr[0]])
        message['Subject'] = Header('来自%s...' % self.__sender_name, 'utf-8')

        # 设置服务参数
        server = smtplib.SMTP(self.__smtp_host, self.__smtp_port)
        server.set_debuglevel(1)
        server.login(self.__smtp_user, self.__smtp_pass)
        server.sendmail(self.__smtp_user, self.__to_addr, message.as_string())
        server.quit()
