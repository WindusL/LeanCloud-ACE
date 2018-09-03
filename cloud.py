#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import os
import logging
import leancloud
from utils.mail.mail_smtp import MailSMTP
from leancloud import Engine
from leancloud import LeanEngineError

engine = Engine()
logging.basicConfig(level=logging.DEBUG)
smtp_user = os.environ['SMTP_USER']


# @engine.define
# def hello(**params):
#     if 'name' in params:
#         return 'Hello, {}!'.format(params['name'])
#     else:
#         return 'Hello, LeanCloud!'
#
#
@engine.before_save('Comment')
def before_todo_save(comment):
    comment_mail = comment.get('mail')
    comment_nick = comment.get('nick')

    logging.debug('评论人［%s］<------>评论邮箱［%s］' % (comment_nick, comment_mail))
    if comment_mail.strip() == "" or comment_nick == "Anonymous":
        raise LeanEngineError(message='评论必填项为空')


@engine.after_save('Comment')  # Comment 为需要 hook 的 class 的名称
def after_comment_save(comment):
    try:
        # 发送邮件
        logging.debug('>>>>>>>>>>>>>>开始发送评论邮件提醒<<<<<<<<<<<<<<<<<%s' % comment)
        comment_mail_transfer(comment)
    except leancloud.LeanCloudError:
        raise LeanEngineError(message='An error occurred while trying to save the Post. ')


# 评论邮件发送封装
def comment_mail_transfer(comment):
    # # @匹配用户名正则
    # comp = re.compile(r'(?<=@)\S+(?=\s)')
    msg = comment.get('comment')
    # at_search = re.search(comp,msg)
    # logging.debug('>>>>>>>>>>>>>>>>>>正则@匹配结果：<<<<<<<<<<<<<<<<<<<\n%s' % at_search)

    to_addr = []  # 邮件接收地址
    comment_mail = comment.get('mail')
    reply_id = comment.get('rid')  # 回复ID
    parent_id = comment.get('pid')  # 回复父ID

    if reply_id is not None:  # 回复评论
        # 查询用户表(需要打开用户表查询权限)
        # User = leancloud.Object.extend('_User')
        # query = User.query
        # query.equal_to('username',at_search.group())
        # query_user = query.first()

        reply_comment = leancloud.Query('Comment').get(reply_id)
        reply_mail = reply_comment.get('mail')
        logging.debug('>>>>>>>>>>>>>>>>>>>>被回复人邮箱[%s]<<<<<<<<<<<<<<' % reply_mail)
        if reply_mail and reply_mail != smtp_user and reply_mail != comment_mail:
            to_addr.append(reply_mail)

    if parent_id != reply_id:
        parent_comment = leancloud.Query('Comment').get(parent_id)
        parent_mail = parent_comment.get('mail')
        logging.debug('>>>>>>>>>>>>>>>>>>>>被回复人父邮箱[%s]<<<<<<<<<<<<<<' % parent_mail)
        if parent_mail and parent_mail != smtp_user and parent_mail != comment_mail:
            to_addr.append(parent_mail)

    if comment_mail != smtp_user:
        to_addr.append(smtp_user)

    logging.debug('>>>>>>>>>>>>>>>>>>>邮件接收列表%s<<<<<<<<<<<<<<<<<<<<' % to_addr)

    # 发送邮件
    if len(to_addr) != 0:
        mail_smtp = MailSMTP(to_addr)
        mail_smtp.send_mail(
            '<p>%s:<p/>%s<br/><a href="%s%s#vcomments" style="display: inline-block; padding: 10px 20px; border-radius: 4px; background-color: #3090e4; color: #fff; text-decoration: none;">马上查看</a></p>' % (
                comment.get('nick'), msg, os.environ['SITE_URL'], comment.get('url')))
