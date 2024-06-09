'''
coding:utf-8
@FileName:run
@Time:2024/5/3 12:55 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''

from crawler.fanqie_crawler import *
from datetime import datetime
import schedule
from dbtuils import *
from factory import assembler



def get_unturnover_video():
    # 从数据库中获取未归档的视频
    db = DButils()
    logger.putback_logger.info('start DB connection')
    try:
        crawler = fanqie_crawler()
        db_name = config.DB_NAME.get('video_record')
        sql = f'select * from {db_name} where is_turnback = 0'
        db.cursor.execute(sql)
        rs = db.cursor.fetchall()
        logger.putback_logger.info(f'get %s unturnover video' % len(rs))
        for r in rs:
            id = r[0]
            send_time = r[1]
            video_id = r[2]
            book_id = r[3]
            publish_time_str = r[13]
            alias = r[9]
            if publish_time_str == '0':

                publish_time_str = send_time
            publish_time = datetime.strptime(publish_time_str,'%Y-%m-%d %H:%M:%S')
            if datetime.now() < publish_time:
                logger.putback_logger.info(f'video %s,bookid %s is not published yet' % (video_id,book_id))
                continue
            logger.putback_logger.info(f'start putback video %s to the bookid %s in fanqie' % (video_id,book_id))
            result = crawler.turn_back(book_id=book_id,alias=alias, video_id=video_id)
            if result:
                sql_update = f'update {db_name} set is_turnback = 1 where id = {id}'
                db.cursor.execute(sql_update)
                db.db.commit()
                logger.putback_logger.info('successfully putback video link : %s to the bookid %s in fanqie' % (video_id,book_id))
    except Exception as e:
        logger.putback_logger.error('error in get_unturnover_video')
        logger.putback_logger.error(e,exc_info=True)
    finally:
        db.close()
        logger.putback_logger.info('db connection is closed')



def schedual_task():
    logger.putback_logger.info("scheduled task executed!")
    # 每五分钟执行一次
    schedule.every().hours.do(get_unturnover_video)


    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == '__main__':
    schedual_task()

    # get_unturnover_video()

    # crawler = fanqie_crawler()
    # crawler.turn_back(bookid=7173533120174492704, video_id=7364218817570000138)