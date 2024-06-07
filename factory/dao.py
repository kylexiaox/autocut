'''
coding:utf-8
@FileName:dao
@Time:2024/5/27 12:31 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''
from functools import wraps

import redis

from dbtuils import *


# 单例装饰器
def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class TaskQueue():

    def __init__(self):
        self.queue = []

    # 把item加入队列，并返回item对应的index
    def push(self, item):
        self.queue.append(item)
        return len(self.queue) - 1

    # 从队列中取出某个具体index对应的item
    def pop(self, index):
        return self.queue.pop(index)

    # 获取全部队列内容
    def get_all(self):
        return self.queue


# 实例化任务队列
tasks = TaskQueue()

# 连接到 Redis 服务器
r = redis.StrictRedis(host='localhost', port=6379, db=0)


def get_task_list(gap_day=3, account_name=None,publish_type = None):
    """
    获取最近days天的任务列表
    :return:
    """
    result = []
    # 去处已入库的任务，FROM DB

    # sql，取出最近days天的任务,对比字段是send_time,send_time的类型是字符串
    if publish_type is None or publish_type == 'published':
        try:
            db = DButils()
            db_name = config.DB_NAME.get('video_record')
            sql = f"SELECT * FROM {db_name}  WHERE DATEDIFF(CURDATE(), STR_TO_DATE(send_time, '%Y-%m-%d')) <= {gap_day} "
            if account_name and account_name != 'all':
                account_id = config.account.get(account_name).get('account_id')
                sql += f"AND account_id = {account_id}"
            # 按照时间降序排列
            sql += " ORDER BY STR_TO_DATE(send_time, '%Y-%m-%d') DESC"
            # 执行sql
            db.cursor_d.execute(sql)
            res = db.cursor_d.fetchall()
            for re in res:
                re['publish_type'] = 'published'
                re.pop('id')
                # 剔除key = id的字段
                result.append(re)
        except Exception as e:
            logger.assemble_logger.error(f'get task list error:{e}')
        finally:
            db.close()

    if publish_type == 'unpublished' or publish_type is None:
        # 从redis中取出最近days天的任务, FROM REDIS
        # 连接到 Redis 服务器
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        messages = r.xrange('task_queue', '-', '+', count=1000)
        for message in messages:
            message = message[1]
            # 遍历dict,将bytes转为str
            new_message = {}
            for key in message.keys():
                new_key = key.decode('utf-8')
                new_message[new_key] = message[key].decode('utf-8')
            new_message['publish_type'] = 'unpublished'
            new_message['video_id'] = ''
            new_message['account_id'] = new_message['account']
            new_message.pop('account')
            new_message['content_description'] = new_message['description']
            new_message.pop('description')
            result.append(new_message)

    if publish_type == 'pre_publish' or publish_type is None:
        # 从任务队列中取出最近days天的任务, FROM TASK QUEUE
        for task in tasks.get_all():
            new_task = {}
            new_task['publish_type'] = 'pre_publish'
            new_task['book_id'] = task['book_id']
            new_task['publish_time'] = task['publish_time']
            new_task['video_id'] = ''
            new_task['account_id'] = config.account.get(task['account_name']).get('account_id')
            new_task['content_description'] = ''
            new_task['send_time'] = ''
            result.append(new_task)

    return result


def check_dumplicate(book_id, account_name, gap_day=30):
    """
    检查是否在gapday天内有重复的任务
    :param book_id:
    :param account_id:
    :return:
    """
    logger.assemble_logger.info(f'check duplicate book_id:{book_id},account_name:{account_name}')
    account_id = config.account.get(account_name).get('account_id')
    sql = f'select * from video_record where book_id = {str(book_id)} and account_id = {str(account_id)}  and DATEDIFF(CURDATE(), STR_TO_DATE(send_time, \'%Y-%m-%d\')) <= {str(gap_day)}'
    db = DButils()
    db.cursor_d.execute(sql)
    res = db.cursor_d.fetchall()
    if len(res) > 0:
        logger.assemble_logger.info(
            f'book_id:{str(book_id)},account_name:{account_name} is duplicate cause has duplicate task in DB')
        return True
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    messages = r.xrange('task_queue', '-', '+', count=1000)
    for message in messages:
        message = message[1]
        new_message = {}
        for key in message.keys():
            new_key = key.decode('utf-8')
            new_message[new_key] = message[key].decode('utf-8')
        if new_message['book_id'] == str(book_id) and new_message['account'] == str(account_id):
            logger.assemble_logger.info(
                f'book_id:{str(book_id)},account_name:{account_name} is duplicate cause has duplicate task in redis')
            return True
    tasks_obj = tasks.get_all()
    for task in tasks_obj:
        if task['book_id'] == book_id and task['account_name'] == account_name:
            logger.assemble_logger.info(
                f'book_id:{str(book_id)},account_name:{account_name} is duplicate cause has duplicate task in task queue')
            return True
    logger.assemble_logger.info(f'book_id:{str(book_id)},account_name:{account_name} is not duplicate')
    return False




if __name__ == '__main__':
    get_task_list(3, 'douyin_nv1')
    print(check_dumplicate(7366928703491670590, 'douyin_nv1'))
