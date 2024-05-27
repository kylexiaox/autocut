'''
coding:utf-8
@FileName:logger
@Time:2023/3/4 00:43
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
日志工具
'''

import os
import logging
import logging.handlers
from datetime import datetime
import coloredlogs
from queue import Queue

import config

# 创建一个队列，用于存储日志消息
log_queue = Queue()


def get_logger(name):
    # 创建日志文件
    name = name.replace(".py", "")
    root_path, file_name = os.path.split(os.path.realpath(__file__))
    log_dir = os.path.join(root_path, './logs')
    create_log_dir(log_dir)

    # 定义日志输出格式
    logger_format = '%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s -%(threadName)s - %(message)s'
    formats = logging.Formatter(logger_format)

    # 定义输出日志级别
    _logger = logging.getLogger('{}_{}'.format(name, datetime.now().strftime('%Y%m%d')))
    _logger.setLevel(logging.DEBUG)

    # 创建一个 coloredlogs 格式化器，并定义不同等级的颜色
    formatter = config.formatter
    # 按指定格式输出到文件
    file_name = os.path.join(log_dir, '{}.log'.format(name))
    fh = file_handler(file_name, formats)
    _logger.addHandler(fh)

    # 按指定格式输出到控制台
    sh = stream_handler(formatter)

    _logger.addHandler(sh)
    fh.close()
    sh.close()
    return _logger


def file_handler(file_name, formats):
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=file_name, when='D', backupCount=7, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formats)
    return file_handler


def stream_handler(formats):
    stream_headler = logging.StreamHandler()
    stream_headler.setLevel(logging.DEBUG)
    stream_headler.setFormatter(formats)
    return stream_headler


def web_handler(formats,handler,clientid):
    web_handler = logging.StreamHandler()
    web_handler.setLevel(logging.DEBUG)
    web_handler.setFormatter(formats)
    web_handler.set_name(clientid)
    # 自定义处理方式，将日志消息发送到队列
    def custom_emit(record):
        handler.send_message(message=record.getMessage(),client_id=clientid)
    web_handler.emit = custom_emit
    return web_handler

def inject_web_handler(hanler,clientid):
    wh = web_handler(config.formatter,hanler,clientid)
    assemble_logger.addHandler(wh)
    wh.close()

def revmove_web_handler(clientid):
    for h in assemble_logger.handlers:
        if h.name == clientid:
            assemble_logger.removeHandler(h)
            h.close()



def create_log_dir(log_dir):
    log_dir = os.path.expanduser(log_dir)
    if not os.path.exists(log_dir) or not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    return


assemble_logger = get_logger('assemble')
putback_logger = get_logger('putback')

