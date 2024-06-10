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

from crawler.qqdoc import get_docs
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
        self.clients[self.client_id] = self
        print(f"WebSocket opened for clientId: {self.client_id}")
        self.heartbeat_timeout = None
        self.reset_heartbeat()

    def on_message(self, message):
        data = json.loads(message)
        if data.get('type') == 'heartbeat':
            print(f"Heartbeat received from clientId: {self.client_id}")
            self.reset_heartbeat()
        else:
            # Handle other types of messages
            pass

    def on_close(self):
        print(f"WebSocket closed for clientId: {self.client_id}")
        if self.heartbeat_timeout:
            self.heartbeat_timeout.cancel()

    def reset_heartbeat(self):
        if self.heartbeat_timeout:
            self.heartbeat_timeout.cancel()
        self.heartbeat_timeout = tornado.ioloop.IOLoop.current().call_later(45, self.close_connection)

    def close_connection(self):
        print(f"Heartbeat lost for clientId: {self.client_id}, closing connection.")
        self.close()

    @classmethod
    def send_message(cls, client_id, message):
        client = cls.clients.get(client_id)
        client = cls.clients.get(client_id)
        if client:
            try:
                client.write_message(message)
            except Exception as e:
                logger.assemble_logger.error(f"Failed to send message to client {client_id}: WebSocket is closed.")




class MainHandler(tornado.web.RequestHandler):
    def get(self):
        bgms = [name for name in os.listdir(config.bgm_directory) if
                os.path.isdir(os.path.join(config.bgm_directory, name))]
        self.render("index.html", account_options=config.account, bgm_options=bgms)


class TaskDocHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("tasks_from_doc.html")


class TaskListHandler(tornado.web.RequestHandler):
    def get(self):
        account_name = self.get_argument('account_name', None)
        gap_day = self.get_argument('gap_day', 3)
        logger.assemble_logger.info(f'account_name:{account_name},gap_day:{gap_day}')
        if account_name is None:
            task_list = []
        else:
            # 获取任务列表
            task_list = get_task_list(gap_day, account_name)
        logger.assemble_logger.info(f'get :{len(task_list)} items')
        self.render("task_list.html", task_list=task_list, account_name=account_name, gap_day=gap_day,
                    account_options=config.account)


class TaskHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @tornado.gen.coroutine
    def post(self):
        try:
            book_id = self.get_argument('bookid')
            bgm_name = self.get_argument('bgm_name')
            account_name = self.get_argument('account')
            publish_time = self.get_argument('publish_time')
            is_summary = self.get_argument('is_summary', '1')
            if publish_time != '0':
                publish_time = publish_time.replace('T', ' ')
            if is_summary == '1':
                is_summary = True
            elif is_summary == '0':
                is_summary = False
            client_id = self.get_argument('clientId')

            logger.inject_web_handler(WebSocketHandler, client_id, ws_logger)
            WebSocketHandler.send_message(client_id, f"this is main thread {time.time()}")
            logger.assemble_logger.info(
                f'Starting video output for {account_name}, book ID: {book_id}, BGM: {bgm_name}, publish time: {publish_time}')

            future = tornado.ioloop.IOLoop.current().run_in_executor(
                self.executor,
                video_output,
                account_name,
                book_id,
                publish_time,
                bgm_name,
                False,  # 是否测试
                True,  # 是否需要推送到MQ
                is_summary  # 是否摘要到单独处理
            )

            result = yield future  # 等待任务完成
            if not result:
                logger.assemble_logger.info(f'Task ended cause of duplicate')
                return self.write("Task ended cause of duplicate")
            logger.assemble_logger.info(f'Task successfully completed')
            self.write("Task successfully completed")
        except Exception as e:
            logger.assemble_logger.error(f'Error occurred: {e}', exc_info=True)
            self.write("Task Ended with Error")
        finally:
            logger.revmove_web_handler(client_id, assemble_logger)
            self.finish()


class DocToListHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def post(self):
        try:
            doc_url = self.get_argument('url')
            tasklist = get_docs(doc_url)
        except Exception as e:
            logger.assemble_logger.error(f'Error occurred: {e}', exc_info=True)
            tasklist = []
        finally:
            result = json.dumps(tasklist, ensure_ascii=False)
            # 设置响应头的 Content-Type 为 application/json
            self.set_header("Content-Type", "application/json")
            print(result)
            self.set_status(200)
            self.write(result)
            self.finish()


class ProcessTasksHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @tornado.gen.coroutine
    def post(self):
        try:
            payload = json.loads(self.request.body)
            clientId = payload.get('clientId')
            tasks = payload.get('tasks')
            logger.inject_web_handler(WebSocketHandler, clientId, ws_logger)

            # 处理tasks和clientid
            print(f"Processing tasks for clientid: {clientId}")

            def process_tasks(tasks):
                for task in tasks:
                    print(f"Processing task: {task}")
                    account_name = task.get('account_name')
                    book_id = task.get('book_id')
                    bgm_name = task.get('bgm_name')
                    publish_time = task.get('publish_time')
                    is_summary = task.get('is_summary')
                    account_id = config.account.get(account_name).get('account_id')
                    taskid = str(account_id) + str(book_id)
                    message_dict = {'taskid': taskid, 'message': f'开始处理任务'}
                    logger.ws_logger.info(json.dumps(message_dict))
                    try:
                        video_output(account_name=account_name, bookid=book_id, publish_time=publish_time,
                                     bgm_name=bgm_name,
                                     is_test=False, is_push=True, is_summary=is_summary)
                        time.sleep(1)
                    except Exception as e:
                        message_dict = {'taskid': taskid, 'message': f'任务处理失败:{e}'}
                        logger.ws_logger.error(json.dumps(message_dict))
                        continue
                    message_dict = {'taskid': taskid, 'message': f'任务处理成功'}
                    logger.ws_logger.error(json.dumps(message_dict))
                return True

            future = tornado.ioloop.IOLoop.current().run_in_executor(
                self.executor,
                process_tasks,
                tasks
            )

            yield future  # 等待任务完成

            self.write(json.dumps({"status": "success", "message": "Tasks processed successfully"}))
        except json.JSONDecodeError:
            self.set_status(400)
            self.write(json.dumps({"status": "error", "message": "Invalid JSON"}))
        finally:
            logger.revmove_web_handler(clientId, assemble_logger)
            self.finish()


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/form", TaskHandler),
        (r"/ws", WebSocketHandler),
        (r"/list", TaskListHandler),
        (r"/form_by_doc", DocToListHandler),
        (r"/tasks_from_doc", TaskDocHandler),
        (r"/process_tasks", ProcessTasksHandler),

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
    tornado.ioloop.IOLoop.current().call_later(3600000,
                                               lambda: ("Database access completed:", DButils().refresh.completed))

    tornado.ioloop.IOLoop.current().start()
