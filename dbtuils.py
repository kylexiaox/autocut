'''
coding:utf-8
@FileName:dbtuils
@Time:2024/5/2 11:36 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''


import pymysql

import logger
from config import *
import config


def singleton(cls, *args, **kwargs):
    """单例方法"""
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


@singleton
class DButils():

    def __init__(self):
        self.db = pymysql.connect(**DB_CONFIG)
        self.cursor = self.db.cursor()
        self.cursor_d = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        sql_database = 'use douyin;'
        self.cursor.execute(sql_database)

    def refresh(self):
        logger.assemble_logger.info('refresh database connection')
        try:
            sql_database = f'use douyin;'
            self.cursor.execute(sql_database)
            print('database connection is ok')
        except Exception as e:
            self.db = pymysql.connect(**DB_CONFIG)
            self.cursor = self.db.cursor()
            self.cursor_d = self.db.cursor(cursor=pymysql.cursors.DictCursor)
            print('reboot database connection')





db: DButils = DButils()