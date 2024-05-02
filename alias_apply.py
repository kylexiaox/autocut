'''
coding:utf-8
@FileName:alias_apply
@Time:2024/1/28 8:22 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''

import requests

headers = {
        'Cookie': 's_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; passport_csrf_token=2706bf1bd3da8c6b603bac3d542accd7; passport_csrf_token_default=2706bf1bd3da8c6b603bac3d542accd7; n_mh=iY4X6u7l6MlRNo51VeHduV1Y0ma-JlIjJ0l81ei6IBA; passport_auth_status=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; passport_auth_status_ss=bc8bde9452bbbd36fd89298ba1b1b4e0%2C; sid_guard=30fa1fc621134e8c93a7d4a7f0b2a6c9%7C1704895474%7C5184000%7CSun%2C+10-Mar-2024+14%3A04%3A34+GMT; uid_tt=41d3dbc571bd8669bcb8c5f428ca6667; uid_tt_ss=41d3dbc571bd8669bcb8c5f428ca6667; sid_tt=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid=30fa1fc621134e8c93a7d4a7f0b2a6c9; sessionid_ss=30fa1fc621134e8c93a7d4a7f0b2a6c9; sid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; ssid_ucp_v1=1.0.0-KDUzMWMyODdhODljMjYwNjkyNTYzYTlmMzgzNWZlZmFlMjMwYzVkMmMKGAigitDb3s2YBRDyx_qsBhjj9xs4AkDxBxoCbHEiIDMwZmExZmM2MjExMzRlOGM5M2E3ZDRhN2YwYjJhNmM5; store-region=cn-sh; store-region-src=uid; x-jupiter-uuid=17056753799365136; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; msToken=VFH0d7_yVqMP_591hkIyqtcTuhBcVazH00elNGsW3RpEiwuhEuhbmHsNCJfzFGdKXWef5WLAysXj9iTfNlU738vKF9lDMj2mw4KKpRD1B8x9Dz2oNaUcy5dDFHu7Y7o=; msToken=NSRSqaQS23-pUEY2I73F19Yi6nzSoXGWVdkR1ieADrvbRXu336_LjfOmEzrskR0MKEmQseXoQP6h6IPn2C_JZPtL34NOrptu_YFKQ3jZryzHRxJbXwAQcw6oPuhAYgQ=; s_v_web_id=verify_lr7upry6_vT8tlt3U_3G0v_4sPH_9oN0_pxyL2UuGgqPj; tt_scid=Ln2B2MJ5yRGWSMw2RxYGaDSdlL36kSwU99jglWmX9WvsYTTYsMk2A64YWMkK9Wvi2cac; x-jupiter-uuid=17056753799365136'
    }

def apply_alias_fanqie(bookid,alias_name):
    url = 'https://kol.fanqieopen.com/api/platform/promotion/plan/create/v:version?app_id=457699&msToken=UEZMgJ5KwQVzidk0KggLrUssZyU04vT7U1plZbVyVYAGOARpVZ6GUj44oLQuwXHUkaxvTxbNIBvvVJgiQDsdjF32iiUiw_yUoO4zAW51Kmhct4UcglSE-5J3aA7kJi5E&X-Bogus=DFSzswVLwTKVD4XYtEQdzjLNKBT/'
    payload = '{"book_id":"'+str(bookid)+'","alias_type":1,"alias_name":"'+alias_name+'"}'
    payload = payload.encode('UTF-8')
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.text)



if __name__ == '__main__':
    apply_alias_fanqie(7303477833404580388,'初心不许他人')