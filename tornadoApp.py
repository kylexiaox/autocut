'''
coding:utf-8
@FileName:tornadoApp
@Time:2024/5/26 2:57 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''


import tornado.ioloop
from tornado import gen
from tornado.ioloop import PeriodicCallback
from concurrent.futures import ThreadPoolExecutor
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import tornado.web
import tornado.websocket
import tornado.escape
import os
import sys
import logger
import asyncio
from dbtuils import *
import io
import time

# 添加项目根目录到 Python 路径
from factory.dao import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'autocut')))
from factory.assembler import *
from logger import *
from config import *


# WebSocket 处理程序
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}

    def open(self):
        self.client_id = self.get_argument('clientId')
        WebSocketHandler.clients[self.client_id] = self
        print(f"WebSocket connection opened with clientId: {self.client_id}")

    def on_close(self):
        if self.client_id in WebSocketHandler.clients:
            del WebSocketHandler.clients[self.client_id]
        print(f"WebSocket connection closed for clientId: {self.client_id}")

    @classmethod
    def send_message(cls, client_id, message):
        client = cls.clients.get(client_id)
        if client:
            client.write_message(message)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        bgms = [name for name in os.listdir(config.bgm_directory) if
                os.path.isdir(os.path.join(config.bgm_directory, name))]
        self.render("index_tornado.html", account_options=config.account, bgm_options=bgms)


class TaskListHandler(tornado.web.RequestHandler):
    def get(self):
        account_name = self.get_argument('account_name',None)
        gap_day = self.get_argument('gap_day',3)
        logger.assemble_logger.info(f'account_name:{account_name},gap_day:{gap_day}')
        if account_name is None:
            task_list = []
        else:
            # 获取任务列表
            task_list = get_task_list(gap_day, account_name)
        logger.assemble_logger.info(f'get :{len(task_list)} items')
        self.render("task_list.html", task_list=task_list,account_name=account_name,gap_day=gap_day,account_options=config.account)



class FormHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @tornado.gen.coroutine
    def post(self):
        try:
            book_id = self.get_argument('bookid')
            bgm_name = self.get_argument('bgm_name')
            account_name = self.get_argument('account')
            publish_time = self.get_argument('publish_time')
            if publish_time != '0':
                publish_time = publish_time.replace('T', ' ')
            client_id = self.get_argument('clientId')

            if publish_time != '0':
                publish_time = publish_time.replace('T', ' ')
            logger.inject_web_handler(WebSocketHandler,client_id)
            WebSocketHandler.send_message(client_id,f"this is main thread {time.time()}")
            logger.assemble_logger.info(
                f'Starting video output for {account_name}, book ID: {book_id}, BGM: {bgm_name}, publish time: {publish_time}')
            # 封装task dict
            task = {
                'account_name': account_name,
                'book_id': book_id,
                'publish_time': publish_time
            }
            # 把task添加到列表里，并返回index
            task_idx = tasks.push(task)
            logger.assemble_logger.info(f'Task added to queue, index: {task_idx}')
            future = tornado.ioloop.IOLoop.current().run_in_executor(
                self.executor,
                video_output,
                account_name,
                book_id,
                publish_time,
                bgm_name,
                False,  # 是否测试
                True  # 是否需要推送到MQ
            )

            result = yield future  # 等待任务完成
            if not result:
                logger.assemble_logger.info(f'Task ended cause of duplicate')
                return self.write("Task ended cause of duplicate")
            logger.assemble_logger.info(f'Task successfully completed')
            self.write("Task successfully completed")
        except Exception as e:
            logger.assemble_logger.error(f'Error occurred: {e}',exc_info=True)
            self.write("Task Ended with Error")
        finally:
            tasks.pop(task_idx)
            logger.assemble_logger.info(f'Task removed from queue, index: {task_idx}')
            logger.revmove_web_handler(client_id)
            self.finish()




def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/form", FormHandler),
        (r"/ws", WebSocketHandler),
        (r"/list", TaskListHandler),
    ], template_path=os.path.join(os.path.dirname(__file__), "html"))


if __name__ == "__main__":

    # 使用 AnyThreadEventLoopPolicy 确保在多线程中正确使用 asyncio
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    app = make_app()
    app.listen(8888)  # 监听端口 8888
    print("WebSocket server started at port 8888")
    # 每小时轮询数据库
    periodic_callback = PeriodicCallback(DButils().refresh, 3600000)
    periodic_callback.start()

    # 这里是检查标记的示例
    tornado.ioloop.IOLoop.current().call_later(3600000, lambda: ("Database access completed:", DButils().refresh.completed))

    tornado.ioloop.IOLoop.current().start()
