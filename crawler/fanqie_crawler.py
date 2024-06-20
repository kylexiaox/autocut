'''
coding:utf-8
@FileName:text
@Time:2024/1/19 10:38 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
get text from website
'''
import re

from bs4 import BeautifulSoup

from crawler.dub import *
import config
from crawler import crawler
from functools import wraps
from factory.utils import *
import time
import logger


def retry(max_retries=3, delay=1):
    """
    重试decorate 方法
    :param max_retries:
    :param delay:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.assemble_logger.error(f"Exception caught: {e}. Retrying...",exc_info=True)
                    attempts += 1
                    time.sleep(delay)
            raise Exception(f"Max retries ({max_retries}) exceeded.")
        return wrapper
    return decorator

class fanqie_crawler(crawler.crawler):

    def __init__(self):
        self.headers = {
                # 'Cookie': 's_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; passport_csrf_token=2706bf1bd3da8c6b603bac3d542accd7; passport_csrf_token_default=2706bf1bd3da8c6b603bac3d542accd7; n_mh=iY4X6u7l6MlRNo51VeHduV1Y0ma-JlIjJ0l81ei6IBA; passport_auth_status=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; passport_auth_status_ss=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; sid_guard=30fa1fc621134e8c93a7d4a7f0b2a6c9%7C1704895474%7C5184000%7CSun%2C+10-Mar-2024+14%3A04%3A34+GMT; uid_tt=41d3dbc571bd8669bcb8c5f428ca6667; uid_tt_ss=41d3dbc571bd8669bcb8c5f428ca6667; sid_tt=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid_ss=30fa1fc621134e8c93a7d4a7f0b2a6c9; sid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; ssid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; store-region=cn-sh; store-region-src=uid; x-jupiter-uuid=17056753799365136; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=; msToken=NSRSqaQS23-pUEY2I73F19Yi6nzSoXGWVdkR1ieADrvbRXu336_LjfOmEzrskR0MKEmQseXoQP6h6IPn2C_JZPtL34NOrptu_YFKQ3jZryzHRxJbXwAQcw6oPuhAYgQ=; s_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; x-jupiter-uuid=17056753799365136'
                'Cookie': config.cookies['kol_fanqie'],
                'Content-Type': 'application/json'
        }

        # self.ms_token = "ReZw6J1Yk3DL7N9V6H9NdZ1mSzfHlw9SD82bnIiYxn0JswmiIQj526rp6UY962mIxasjJK-W4ZvkR0hyfCX4hscO45RoV1FRljvJXyU7ixMyGz8594JOOReL3i8jC9mN&X-"
        self.ms_token = "MtJ2GFZizX7YYAWtQn_hzji-JELIYRBUcdA2rWeM-hWVKHVcHb4zqcwbQtdqAn-mJHlOSvJ00cNldlGeYVgcXmGnLTLJF3DI8H7hjgiNv8YY5BQudaIBEF4ThkLboCtEUQ=="
        self.x_bogus = "DFSzswVLA4uTIRhCtRQSzELNKBOp"

    @retry()
    def get_book_info(self,book_id,content_type = 8):
        '''
        拿书籍信息
        :param book_id:
        :param content_type: 0是长篇，8是短片
        :return:
        '''
        url = 'https://kol.fanqieopen.com/api/platform/content/book/list/v:version?book_id='+str(book_id)+'&content_tab=2&genre='+str(content_type)+'&app_id=457699&msToken='+self.ms_token+'&X-Bogus='+self.x_bogus
        response = requests.request('GET',url,headers=self.headers)
        raw_resposne = response.text
        json_resposne = json.loads(raw_resposne)
        book_name = json_resposne['data']['book_list'][0]['book_name']
        abstract = json_resposne['data']['book_list'][0]['book_abstract']
        return book_name,abstract,book_id

    @retry()
    def get_first_itemid(self,book_id):
        """
        拿第一章
        :param book_id:
        :return:
        """

        url = 'https://kol.fanqieopen.com/api/platform/content/chapter/list/v:version?book_id='+str(book_id)+'&page_index=0&page_size=500&content_tab=2&app_id=457699&msToken='+self.ms_token+'&X-Bogus='+self.x_bogus
        payload = {}
        response = requests.request("GET", url, headers=self.headers, data=payload)
        raw_response = response.text
        json_response = json.loads(raw_response)
        logger.assemble_logger.info('第一章内容返回对象为：'+str(json_response))
        item_id = json_response['data']['chapter_list'][0]['item_id']
        return item_id

    @retry()
    def get_items(self,book_id):
        """
        拿所有的章节列表，返回json对象
        :param book_id:
        :return:
        """
        url = 'https://kol.fanqieopen.com/api/platform/content/chapter/list/v:version?book_id='+str(book_id)+'&page_index=0&page_size=500&content_tab=2&app_id=457699&msToken='+self.ms_token+'&X-Bogus='+self.x_bogus
        payload = {}
        response = requests.request("GET", url, headers=self.headers, data=payload)
        raw_response = response.text
        json_response = json.loads(raw_response)
        item_ids = json_response['data']['chapter_list']
        return item_ids

    @retry()
    def get_content_from_fanqie_dp(self,book_id,is_summary = True):
        """
        拿短篇内容
        :param book_id:
        :return:
        """
        item_id = self.get_first_itemid(book_id)
        url = 'https://kol.fanqieopen.com/api/platform/content/chapter/detail/v:version?book_id='+str(book_id)+'&item_id='+item_id+'&content_tab=2&app_id=457699&msToken='+self.ms_token+'&X-Bogus='+self.x_bogus
        payload = {}
        response = requests.request("GET", url, headers=self.headers, data=payload)
        raw_response = response.text
        json_response = json.loads(raw_response)
        text_content = json_response['data']['content']
        # 使用 BeautifulSoup 剔除标签
        soup = BeautifulSoup(text_content, 'html.parser')
        summary,content = clean_the_soup_short(soup,is_summary)
        if summary:
            summary = summary.get_text()
        content = content.get_text()

        return summary,content


    @retry()
    def get_content_from_fanqie_long(self,book_id):
        """
        拿长篇内容
        :param book_id:
        :return:
        """
        items = self.get_items(book_id)
        re_texts = []
        for item in items:
            item_id = item.get('item_id')
            url = 'https://kol.fanqieopen.com/api/platform/content/chapter/detail/v:version?book_id=' + str(
                book_id) + '&item_id=' + item_id + '&content_tab=2&app_id=457699&msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=&X-Bogus=DFSzswVus5vANaDttitQWDLNKBTL'
            payload = {}
            response = requests.request("GET", url, headers=self.headers, data=payload)
            raw_response = response.text
            json_response = json.loads(raw_response)
            if json_response['data'] is None:
                break
            text_content = json_response['data']['content']
            # 使用 BeautifulSoup 剔除标签
            soup = BeautifulSoup(text_content, 'html.parser')
            extract_string = soup.get_text()
            cleaned_string = ''.join(remove_non_utf8(char) for char in extract_string)
            re_texts.append(cleaned_string)
        return re_texts


    @retry()
    def turn_back(self,book_id,alias,video_id):
        """
        回填内容链接
        :param book_id:
        :param alias:
        :param video_id:
        :return:
        """
        alais, alais_id = self.get_alias_id(book_id=book_id,alias=alias)
        if alais_id is None:
            return False
        url = 'https://kol.fanqieopen.com/api/platform/promotion/post/create/v:version?app_id=457699&msToken='+self.ms_token+'&X-Bogus='+self.x_bogus
        payload ='{"alias_id":"'+str(alais_id)+'","post_records":[{"post_link":"https://www.douyin.com/video/'+str(video_id)+'"}],"alias_type":1}'
        response = requests.request(method='POST',url=url,headers=self.headers, data=payload)
        if response.status_code == 200:
            raw_response = response.text
            json_response = json.loads(raw_response)
            try:
                code = json_response['code']
                message  = json_response['message']
                # log_id = json_response['log_id']
                if code == 0:
                    return True
                else:
                    raise Exception({'code': code, 'message':message})
            except Exception as e:
                logger.assemble_logger.error(e)
                return False

    @retry()
    def get_alias_id(self,book_id,alias=None):
        """
        获得 bookid、alias 相关的 aliasid，这里alias和aliasid是两件事
        :param book_id:
        :param alias:
        :return:
        """
        url = f'https://kol.fanqieopen.com/api/platform/promotion/plan/list/v:version?book_id={str(book_id)}&task_type=1&page_index=0&page_size=10&app_id=457699&msToken={self.ms_token}&X-Bogus={self.x_bogus}'
        response = requests.get(url,headers = self.headers)
        if response.status_code == 200:
            raw_response = response.text
            json_response = json.loads(raw_response)
            try:
                code = json_response['code']
                message = json_response['message']
                if code != 0:
                    raise Exception({'code': code, 'message':message})
                # log_id = json_response['log_id']
                promotion_list = json_response['data']['promotion_list']
                if alias is None:
                    return promotion_list[0]['alias_name'],promotion_list[0]['alias_id']
                else:
                    for promotion in promotion_list:
                        if alias == promotion['alias_name']:
                            alias_id = promotion['alias_id']
                            return alias, alias_id
            except Exception as e:
                logger.putback_logger.error(e)
                return None



    def apply_alias_fanqie(self,bookid, alias_name):
        """
        申请别名
        :param bookid:
        :param alias_name:
        :return:
        """
        url = 'https://kol.fanqieopen.com/api/platform/promotion/plan/create/v:version?app_id=457699&msToken=UEZMgJ5KwQVzidk0KggLrUssZyU04vT7U1plZbVyVYAGOARpVZ6GUj44oLQuwXHUkaxvTxbNIBvvVJgiQDsdjF32iiUiw_yUoO4zAW51Kmhct4UcglSE-5J3aA7kJi5E&X-Bogus=DFSzswVLwTKVD4XYtEQdzjLNKBT/'
        payload = '{"book_id":"' + str(bookid) + '","alias_type":1,"alias_name":"' + alias_name + '"}'
        payload = payload.encode('UTF-8')
        response = requests.request("POST", url, headers=self.headers, data=payload)
        if response.status_code == 200:
            logger.putback_logger.info(response.text)


def clean_the_soup_short(soup,is_summary=True):
    """
    为番茄短篇清洗soup内容,剔除章节标题
    剔除单行的1、2、3.
    剔除单行的第一章、第二章、第三章等
    并把文本分割，区分为第一章节标题前的内容作为摘要，后面的作为正文内容
    :param soup:
    :param has_summary: 是否有摘要,摘要是否要分割出来 True 为拆，False 为不拆
    :return:
    """
    logger.assemble_logger.info(f"开始处理文本文件，剔除章节标题,并拆解摘要和正文内容...")
    # 编写正则表达式，匹配只含数字、中文数字、"第x章" 格式的内容
    # pattern = re.compile(r'^[0-9一二三四五六七八九十百千万亿]+$|^第[0-9一二三四五六七八九十百千万亿]+章$')
    pattern = re.compile( r'^[0-9一二三四五六七八九十百千万亿，,、．。.\-:：!！?？、]+$|^第[0-9一二三四五六七八九十百千万亿]+章$')
    # 创建两个新的BeautifulSoup对象，一个用于存放摘要内容，一个用于存放正文内容
    summary = BeautifulSoup('', 'html.parser')
    content = BeautifulSoup('', 'html.parser')
    # 剔除匹配到的<p>标签
    for idex, p_tag in enumerate(soup.find_all('p')):
        if pattern.match(p_tag.text.strip()):
            logger.assemble_logger.info(f"处理文本文件，剔除内容：{p_tag.text.strip()}")
            if is_summary and idex > 30:
                logger.assemble_logger.info(f"第一个分隔符超过30行，认为没有摘要...")
                # 并且已经有30个以上的p标签，还没有找到分隔符，那么就认为这本书没有摘要,之前存储的summary都成为征文
                content = summary
                # summary 清空
                summary = None
            is_summary = False

            p_tag.extract()
            continue
        elif is_summary:
            summary.append(p_tag)
        else:
            content.append(p_tag)

    # 循环结束，如果is_summary为True，说明没有找到分隔符，那么将summary内容赋值给content
    if is_summary:
        logger.assemble_logger.info(f"没有找到分隔符，将summary内容赋值给content")
        content = summary
        summary = None
    logger.assemble_logger.info(f"文本文件处理完成，摘要内容：{summary.text.strip()[:10] if summary else ''}...,正文内容：{content.text.strip()[:100]}...")
    return summary, content


if __name__ == '__main__':
    crawler = fanqie_crawler()
    crawler.turn_back(bookid=7173533120174492704,video_id=7364218817570000138)

# #########短篇
#     bookids = [7329015211099161150]
#     for bookid in bookids:
#         bookinfo = get_book_info(bookid)
#         texts = split_content(get_content_from_fanqie_dp(bookid),gap=6000,end_with='。')
#         for index,text in enumerate(texts):
#             dubbing_for_long(long_text=text,result_filename=str(bookinfo[0])+'_'+str(index),voice_type='female')
#         with open(config.audio_directory_short+bookinfo[0]+'.txt', 'wb') as file:
#             info_str = 'book_id : ' + str(bookinfo[2]) +'\n'
#             info_str += 'book_name : ' + bookinfo[0]+'\n'
#             info_str += 'abstract : ' + bookinfo[1]
#             file.write(info_str.encode('UTF-8'))
#
#     # get_itemid(7304472167742180386)
# ##########长篇
#     bookids = [7280064899676376064]
#     for bookid in bookids:
#         bookinfo = get_book_info(bookid,content_type=0)
#         texts = get_content_from_fanqie_long(bookid)
#
#     for index,text in enumerate(texts):
#         dubbing_for_long(long_text=text,result_filename=str(bookinfo[0])+'_'+str(index),voice_type='female',content_type=0)
#     with open(config.audio_directory_long+bookinfo[0]+'.txt', 'wb') as file:
#         info_str = 'book_id : ' + str(bookinfo[2]) +'\n'
#         info_str += 'book_name : ' + bookinfo[0]+'\n'
#         info_str += 'abstract : ' + bookinfo[1]
#         file.write(info_str.encode('UTF-8'))