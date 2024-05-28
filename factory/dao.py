'''
coding:utf-8
@FileName:dao
@Time:2024/5/27 12:31 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''
import redis

from dbtuils import *

# 连接到 Redis 服务器
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_task_list(gap_day=3,account_name=None):
    """
    获取最近days天的任务列表
    :return:
    """
    result = []
    # 连接到 Redis 服务器
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    db_name = config.DB_NAME.get('video_record')
    # sql，取出最近days天的任务,对比字段是send_time,send_time的类型是字符串
    sql = f"SELECT * FROM {db_name}  WHERE DATEDIFF(CURDATE(), STR_TO_DATE(send_time, '%Y-%m-%d')) <= {gap_day} "
    if account_name:
        account_id = config.account.get(account_name).get('account_id')
        sql += f"AND account_id = {account_id}"
    # 按照时间降序排列
    sql += " ORDER BY STR_TO_DATE(send_time, '%Y-%m-%d') DESC"
    # 执行sql
    db.cursor_d.execute(sql)
    res = db.cursor_d.fetchall()
    messages = r.xrange('task_queue', '-', '+', count=1000)
    for re in res:
        re['publish_type'] = 'published'
        # 剔除key = id的字段
        re.pop('id')
        result.append(re)
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
        return result







    #
    # sql = f'select * from {db_name} where datediff(now(),created_at) < %s'
    # return query(sql, (days,))


if __name__ == '__main__':
    get_task_list(gap_day=3,account_name='douyin_nv1')