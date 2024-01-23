'''
coding:utf-8
@FileName:dub
@Time:2024/1/18 11:48 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
文字->音频
'''

import requests
from text import *




headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Access-Token': '5528714820020229',
    'Content-Type': 'application/json;charset=UTF-8'
}

cookies = {
    'Hm_lvt_f5b437a514220b03e07d673baf63f78c': '1705589966',
    'fromId': 'bdbrand',
    'shareToken': '5528714820020229',
    'Hm_lpvt_f5b437a514220b03e07d673baf63f78c': '1705590163'
}



def dubbing_for_long(long_text,voice_type,result_filename):
    """
    长文本
    :param texts:
    :param voice_type:
    :param result_filename:
    :return:
    """

    texts = split_content(long_text,500,'。')

    for index,text in enumerate(texts):
        file_name = result_filename+str(index)+'.mp4'
        dubbing(text,voice_type,file_name)



def dubbing(text, voice_type,result_filename):
    """
    转换音频
    :param text:
    :param voice_type:
    :param result_filename:
    :return:
    """
    # 转换语音最多8000字

    cookies = {
        'Hm_lvt_f5b437a514220b03e07d673baf63f78c': '1705589966',
        'fromId': 'bdbrand',
        'shareToken': '5528714820020229',
        'Hm_lpvt_f5b437a514220b03e07d673baf63f78c': '1705590163'
    }
    url = "https://www.douge.club/peiyin/user/webAudition"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Access-Token': '5528714820020229',
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': 'Cookie_1=value'
    }

    payload = '{"speed":5,"styleDegree":0,"highDensity":0,"text":"' + text + '","voice":"' + voice_type + '","pitch":"0","sign":"3e3d7a1de064eb699daafe3c9a737052b4a58d0dfec6123afa5772e8e5de01600afbedd407bd7a2b974561b9dabd5ab3d521834bffd53b94fcafa6d27ffecb08"}'
    payload = payload.encode('UTF-8')
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.content)
        # 以二进制写模式打开文件，并将响应内容写入文件
        with open(result_filename+'.mp4', 'wb') as file:
            file.write(response.content)
        print(f'音乐文件已成功下载到: {result_filename}')
        return 1
    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 0







