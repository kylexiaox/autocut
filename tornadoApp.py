'''
coding:utf-8
@FileName:tornadoApp
@Time:2024/5/26 2:57 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''
# tornadoApp.py
# tornadoApp.py

import tornado.ioloop
from tornado import gen
from tornado.ioloop import PeriodicCallback
import tornado.web
import tornado.websocket
import tornado.escape
import os
import sys
import logger
from dbtuils import *
import io
import time

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'autocut')))
from factory.assembler import video_output
from logger import *
from config import *

# WebSocket 处理程序
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def open(self):
        WebSocketHandler.clients.add(self)
        print("WebSocket connection opened")

    def on_close(self):
        WebSocketHandler.clients.remove(self)
        print("WebSocket connection closed")

    @classmethod
    def send_message(cls, message):
        for client in cls.clients:
            client.write_message(message)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        bgms = [name for name in os.listdir(config.bgm_directory) if os.path.isdir(os.path.join(config.bgm_directory, name))]
        self.render("index_tornado.html", account_options=config.account, bgm_options=bgms)

class TaskListHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Task list")

class FormHandler(tornado.web.RequestHandler):
    def post(self):
        book_id = self.get_argument('bookid')
        bgm_name = self.get_argument('bgm_name')
        account_name = self.get_argument('account')
        publish_time = self.get_argument('publish_time').replace('T', ' ')
        if publish_time != '0':
            publish_time = publish_time.replace('T', ' ')
        logger.inject_web_handler(WebSocketHandler)
        WebSocketHandler.send_message(f"this is main thread {time.time()}")
        logger.assemble_logger.info(f'Starting video output for {account_name}, book ID: {book_id}, BGM: {bgm_name}, publish time: {publish_time}')
        video_output(account_name, book_id, publish_time, bgm_name)
        self.write("Task started")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/form", FormHandler),
        (r"/ws", WebSocketHandler),
    ], template_path=os.path.join(os.path.dirname(__file__), "html"))

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  # 监听端口 8888
    print("WebSocket server started at port 8888")
    # 每小时轮询数据库
    periodic_callback = PeriodicCallback(db.refresh, 3600000)
    periodic_callback.start()

    # 这里是检查标记的示例
    tornado.ioloop.IOLoop.current().call_later(3600000, lambda: ("Database access completed:", db.refresh.completed))

    tornado.ioloop.IOLoop.current().start()
