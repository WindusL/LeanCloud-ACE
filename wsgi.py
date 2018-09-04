#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from gevent import monkey

monkey.patch_all()

import os

import leancloud

from app import app
from cloud import engine

APP_ID = os.environ['LEANCLOUD_APP_ID']
APP_KEY = os.environ['LEANCLOUD_APP_KEY']
MASTER_KEY = os.environ['LEANCLOUD_APP_MASTER_KEY']
PORT = int(os.environ['LEANCLOUD_APP_PORT'])

leancloud.init(APP_ID, app_key=APP_KEY, master_key=MASTER_KEY)
# 如果需要使用 master key 权限访问 LeanCLoud 服务，请将这里设置为 True
leancloud.use_master_key(False)

# 需要重定向到 HTTPS 可去除下一行的注释。
# app = leancloud.HttpsRedirectMiddleware(app)
app = engine.wrap(app)
application = app

"""
休眠策略-->应用最近一段时间（半小时）没有任何外部请求，则休眠。
强制休眠-->如果最近 24 小时内累计运行超过 18 小时，则强制休眠
设置定时访问服务器做心跳连接
"""
import time
import logging
import threading
from urllib import request

TIMER_SECOND = 1200  # 定时间隔20分钟(1200)
LEAN_SLD = 'http://' + os.environ['LEANCLOUD_APP_DOMAIN'] + '.leanapp.cn'  # lean设置的二级域名

logging.basicConfig(level=logging.DEBUG)


def visit_server():
    with request.urlopen(LEAN_SLD) as req:
        logging.debug('[%s]>>>>>>>>>>>>>>>>>>心跳连接服务器(%s)Status：[%s<---->%s]' % (
            time.strftime('%Y-%m-%d %T'), LEAN_SLD, req.status, req.reason))

    # timmer = threading.Timer(TIMER_SECOND, visit_server)
    # timmer.start()


# timmer = threading.Timer(TIMER_SECOND, visit_server)
# timmer.start()

if __name__ == '__main__':
    # 只在本地开发环境执行的代码
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler
    from werkzeug.serving import run_with_reloader
    from werkzeug.debug import DebuggedApplication


    @run_with_reloader
    def run():
        global application
        app.debug = True
        application = DebuggedApplication(application, evalex=True)
        server = WSGIServer(('localhost', PORT), application, handler_class=WebSocketHandler)
        server.serve_forever()


    run()
