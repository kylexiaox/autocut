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



def get_itemid(book_id):

    url = 'https://kol.fanqieopen.com/api/platform/content/chapter/list/v:version?book_id='+str(book_id)+'&page_index=0&page_size=500&content_tab=2&app_id=457699&msToken=7wANaChBRVJ-FhSjq6v9azPMBbi4SgacaaqHDvSyahB4JYVU89DGHA6AJFsmcYomc_XDasNUllsB7MDXa11hzIxjDDIr6nxEzZv-dXy3klrun3SM_pIF0bGZc7K9YZ0=&X-Bogus=DFSzswVYQvXANVoktitUwELNKBTx'

    payload = {}
    headers = {
        'Cookie': 's_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; passport_csrf_token=2706bf1bd3da8c6b603bac3d542accd7; passport_csrf_token_default=2706bf1bd3da8c6b603bac3d542accd7; n_mh=iY4X6u7l6MlRNo51VeHduV1Y0ma-JlIjJ0l81ei6IBA; passport_auth_status=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; passport_auth_status_ss=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; sid_guard=30fa1fc621134e8c93a7d4a7f0b2a6c9%7C1704895474%7C5184000%7CSun%2C+10-Mar-2024+14%3A04%3A34+GMT; uid_tt=41d3dbc571bd8669bcb8c5f428ca6667; uid_tt_ss=41d3dbc571bd8669bcb8c5f428ca6667; sid_tt=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid_ss=30fa1fc621134e8c93a7d4a7f0b2a6c9; sid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; ssid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; store-region=cn-sh; store-region-src=uid; x-jupiter-uuid=17056753799365136; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; msToken=7wANaChBRVJ-FhSjq6v9azPMBbi4SgacaaqHDvSyahB4JYVU89DGHA6AJFsmcYomc_XDasNUllsB7MDXa11hzIxjDDIr6nxEzZv-dXy3klrun3SM_pIF0bGZc7K9YZ0=; s_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; tt_scid=fGit64rpZ7wJnRJS9l-y7ALwoRphPiAhcwUS.UXrOrSlEZlB.7V-vshoSptiAorBde10; x-jupiter-uuid=17056753799365136'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    raw_response = response.text
    json_response = json.loads(raw_response)
    item_id = json_response['data']['chapter_list'][0]['item_id']
    return item_id

def get_content_from_fanqie(book_id):

    item_id = get_itemid(book_id)

    url = 'https://kol.fanqieopen.com/api/platform/content/chapter/detail/v:version?book_id='+str(book_id)+'&item_id='+item_id+'&content_tab=2&app_id=457699&msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=&X-Bogus=DFSzswVus5vANaDttitQWDLNKBTL'
    payload = {}
    headers = {
        'Cookie': 's_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; passport_csrf_token=2706bf1bd3da8c6b603bac3d542accd7; passport_csrf_token_default=2706bf1bd3da8c6b603bac3d542accd7; n_mh=iY4X6u7l6MlRNo51VeHduV1Y0ma-JlIjJ0l81ei6IBA; passport_auth_status=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; passport_auth_status_ss=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; sid_guard=30fa1fc621134e8c93a7d4a7f0b2a6c9%7C1704895474%7C5184000%7CSun%2C+10-Mar-2024+14%3A04%3A34+GMT; uid_tt=41d3dbc571bd8669bcb8c5f428ca6667; uid_tt_ss=41d3dbc571bd8669bcb8c5f428ca6667; sid_tt=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid_ss=30fa1fc621134e8c93a7d4a7f0b2a6c9; sid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; ssid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; store-region=cn-sh; store-region-src=uid; x-jupiter-uuid=17056753799365136; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=; msToken=NSRSqaQS23-pUEY2I73F19Yi6nzSoXGWVdkR1ieADrvbRXu336_LjfOmEzrskR0MKEmQseXoQP6h6IPn2C_JZPtL34NOrptu_YFKQ3jZryzHRxJbXwAQcw6oPuhAYgQ=; s_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; x-jupiter-uuid=17056753799365136'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    raw_response = response.text
    json_response = json.loads(raw_response)
    text_content = json_response['data']['content']

    # 使用 BeautifulSoup 剔除标签
    soup = BeautifulSoup(text_content, 'html.parser')
    cleaned_string = soup.get_text()

    return cleaned_string


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


if __name__ == '__main__':
    print(get_content_from_fanqie(7304472167742180386))
    # get_itemid(7304472167742180386)