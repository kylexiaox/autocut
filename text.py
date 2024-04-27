'''
coding:utf-8
@FileName:text
@Time:2024/1/19 10:38 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
get text from website
'''
import requests
import json
from bs4 import BeautifulSoup
from dub import *
import config


headers = {
        # 'Cookie': 's_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; passport_csrf_token=2706bf1bd3da8c6b603bac3d542accd7; passport_csrf_token_default=2706bf1bd3da8c6b603bac3d542accd7; n_mh=iY4X6u7l6MlRNo51VeHduV1Y0ma-JlIjJ0l81ei6IBA; passport_auth_status=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; passport_auth_status_ss=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; sid_guard=30fa1fc621134e8c93a7d4a7f0b2a6c9%7C1704895474%7C5184000%7CSun%2C+10-Mar-2024+14%3A04%3A34+GMT; uid_tt=41d3dbc571bd8669bcb8c5f428ca6667; uid_tt_ss=41d3dbc571bd8669bcb8c5f428ca6667; sid_tt=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid_ss=30fa1fc621134e8c93a7d4a7f0b2a6c9; sid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; ssid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; store-region=cn-sh; store-region-src=uid; x-jupiter-uuid=17056753799365136; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=; msToken=NSRSqaQS23-pUEY2I73F19Yi6nzSoXGWVdkR1ieADrvbRXu336_LjfOmEzrskR0MKEmQseXoQP6h6IPn2C_JZPtL34NOrptu_YFKQ3jZryzHRxJbXwAQcw6oPuhAYgQ=; s_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; x-jupiter-uuid=17056753799365136'
        'Cookie': config.cookies['kol_fanqie']
}

ms_token = "ReZw6J1Yk3DL7N9V6H9NdZ1mSzfHlw9SD82bnIiYxn0JswmiIQj526rp6UY962mIxasjJK-W4ZvkR0hyfCX4hscO45RoV1FRljvJXyU7ixMyGz8594JOOReL3i8jC9mN&X-"
x_bogus = "DFSzswVuFvJANjA3tLOaCjLNKBTn"


def get_book_info(book_id,content_type = 8):
    '''
    :param book_id:
    :param content_type: 0是长篇，8是短片
    :return:
    '''
    url = 'https://kol.fanqieopen.com/api/platform/content/book/list/v:version?book_id='+str(book_id)+'&content_tab=2&genre='+str(content_type)+'&app_id=457699&msToken='+ms_token+'&X-Bogus='+x_bogus
    response = requests.request('GET',url,headers=headers)
    raw_resposne = response.text
    json_resposne = json.loads(raw_resposne)
    book_name = json_resposne['data']['book_list'][0]['book_name']
    abstract = json_resposne['data']['book_list'][0]['book_abstract']
    return book_name,abstract,book_id

def get_itemid(book_id):
    # 拿第一章
    url = 'https://kol.fanqieopen.com/api/platform/content/chapter/list/v:version?book_id='+str(book_id)+'&page_index=0&page_size=500&content_tab=2&app_id=457699&msToken='+ms_token+'&X-Bogus='+x_bogus
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    raw_response = response.text
    json_response = json.loads(raw_response)
    item_id = json_response['data']['chapter_list'][0]['item_id']
    return item_id

def get_items(book_id):
    # 拿所有的章节列表，返回json对象
    url = 'https://kol.fanqieopen.com/api/platform/content/chapter/list/v:version?book_id='+str(book_id)+'&page_index=0&page_size=500&content_tab=2&app_id=457699&msToken='+ms_token+'&X-Bogus='+x_bogus
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    raw_response = response.text
    json_response = json.loads(raw_response)
    item_ids = json_response['data']['chapter_list']
    return item_ids

def get_content_from_fanqie_dp(book_id):

    item_id = get_itemid(book_id)

    url = 'https://kol.fanqieopen.com/api/platform/content/chapter/detail/v:version?book_id='+str(book_id)+'&item_id='+item_id+'&content_tab=2&app_id=457699&msToken='+ms_token+'&X-Bogus='+x_bogus

    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    raw_response = response.text
    json_response = json.loads(raw_response)
    text_content = json_response['data']['content']

    # 使用 BeautifulSoup 剔除标签
    soup = BeautifulSoup(text_content, 'html.parser')
    extract_string = soup.get_text()
    # 需要去除文中的分隔符,引号等
    cleaned_string = ''.join([char for char in extract_string if char != '"'])
    cleaned_string = cleaned_string.replace('*','')
    return cleaned_string

def get_content_from_fanqie_long(book_id):

    items = get_items(book_id)
    re_texts = []
    for item in items:
        item_id = item.get('item_id')
        url = 'https://kol.fanqieopen.com/api/platform/content/chapter/detail/v:version?book_id=' + str(
            book_id) + '&item_id=' + item_id + '&content_tab=2&app_id=457699&msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=&X-Bogus=DFSzswVus5vANaDttitQWDLNKBTL'
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)
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

def count_chinese_characters(input_string):
    count = 0
    for char in input_string:
        # 判断字符是否是汉字
        if '\u4e00' <= char <= '\u9fff':
            count += 1
    return count

def split_content(input_string,gap,end_with):
    """
    切割字符串
    :param input_string:
    :param count:
    :param end_with:
    :return:
    """
    print(len(input_string))
    start = 0
    results = []
    for index, char in enumerate(input_string):
        if (index-start) > (gap-50):
            if char == end_with:
                results.append(input_string[start:index+1])
                start = index+1
                continue
            if (index-start) == gap:
                results.append(input_string[start:index+1])
                start = index + 1
                continue
        if index == len(input_string)-1:
            results.append(input_string[start:index+1])
    return results


def remove_non_utf8(s):
    # 尝试将字符串编码为UTF-8，如果失败则捕获UnicodeEncodeError异常
    try:
        s.encode(encoding='utf-8')
        return s
    except UnicodeEncodeError:
        return ''

def trim(s):
    s.replace('*','')
    return s


if __name__ == '__main__':

#########短篇
    bookids = [7329015211099161150]
    for bookid in bookids:
        bookinfo = get_book_info(bookid)
        texts = split_content(get_content_from_fanqie_dp(bookid),gap=6000,end_with='。')
        for index,text in enumerate(texts):
            dubbing_for_long(long_text=text,result_filename=str(bookinfo[0])+'_'+str(index),voice_type='female')
        with open(config.audio_directory_short+bookinfo[0]+'.txt', 'wb') as file:
            info_str = 'book_id : ' + str(bookinfo[2]) +'\n'
            info_str += 'book_name : ' + bookinfo[0]+'\n'
            info_str += 'abstract : ' + bookinfo[1]
            file.write(info_str.encode('UTF-8'))

    # get_itemid(7304472167742180386)
##########长篇
    bookids = [7280064899676376064]
    for bookid in bookids:
        bookinfo = get_book_info(bookid,content_type=0)
        texts = get_content_from_fanqie_long(bookid)

    for index,text in enumerate(texts):
        dubbing_for_long(long_text=text,result_filename=str(bookinfo[0])+'_'+str(index),voice_type='female',content_type=0)
    with open(config.audio_directory_long+bookinfo[0]+'.txt', 'wb') as file:
        info_str = 'book_id : ' + str(bookinfo[2]) +'\n'
        info_str += 'book_name : ' + bookinfo[0]+'\n'
        info_str += 'abstract : ' + bookinfo[1]
        file.write(info_str.encode('UTF-8'))