'''
coding:utf-8
@FileName:dao
@Time:2024/5/27 12:31 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''


from dbtuils import *



def get_task_list(gap_day=3,account_name=None):
    """
    获取最近days天的任务列表
    :return:
    """
    db_name = config.DB_NAME.get('video_record')
    # sql，取出最近days天的任务,对比字段是send_time,send_time的类型是字符串
    sql = f"SELECT * FROM {db_name}  WHERE DATEDIFF(CURDATE(), STR_TO_DATE(send_time, '%Y-%m-%d')) <= {gap_day} "
    if account_name:
        account_id = config.account.get(account_name).get('account_id')
        sql += f"AND account_id = {account_id}"
    # 按照时间降序排列
    sql += " ORDER BY STR_TO_DATE(send_time, '%Y-%m-%d') DESC"
    print(sql)




    #
    # sql = f'select * from {db_name} where datediff(now(),created_at) < %s'
    # return query(sql, (days,))


if __name__ == '__main__':
    get_task_list(gap_day=3,account_name='douyin_nv1')