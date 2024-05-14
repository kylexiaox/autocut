'''
coding:utf-8
@FileName:run
@Time:2024/5/3 12:55 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''
import dbutils.steady_db

from crawler.fanqie_crawler import *
from datetime import datetime
import schedule
from dbtuils import *



def get_unturnover_video():
    crawler = fanqie_crawler()
    db_name = config.DB_NAME.get('video_record')
    sql = f'select * from {db_name} where is_turnback = 0'

    db.cursor.execute(sql)
    rs = db.cursor.fetchall()
    for r in rs:
        id = r[0]
        video_id = r[2]
        book_id = r[3]
        publish_time_str = r[13]
        alias = r[9]
        publish_time = datetime.strptime(publish_time_str,'%Y-%m-%d %H:%M:%S')
        if datetime.now() < publish_time:
            continue
        print(f'putback video %s to the bookid %s in fanqie' % (video_id,book_id))
        result = crawler.turn_back(book_id=book_id,alias=alias, video_id=video_id)
        if result:
            sql_update = f'update {db_name} set is_turnback = 1 where id = {id}'
            db.cursor.execute(sql_update)
            db.db.commit()
            print('successfully putback video link : %s to the bookid %s in fanqie' % (video_id,book_id))



def hourly_task():
    print("Hourly task executed!")
    schedule.every().minute.do(get_unturnover_video)

    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == '__main__':
    hourly_task()
    # get_unturnover_video()

    # crawler = fanqie_crawler()
    # crawler.turn_back(bookid=7173533120174492704, video_id=7364218817570000138)