'''
coding:utf-8
@FileName:dub
@Time:2024/1/18 11:48 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
文字->音频
音频->字幕
'''

import requests
from text import *
import json
from Crypto.Cipher import AES
import base64
import time
import config


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Access-Token': '8910719813414015',
    'Content-Type': 'application/json;charset=UTF-8',
    "Cookie": "shareToken=8910719813414015",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.douge.club/",
}

cookies = {
    'Hm_lvt_f5b437a514220b03e07d673baf63f78c': '1706376932',
    'fromId': 'bdmyzirj',
    'shareToken': '8910719813414015',
    'Hm_lvt_f5b437a514220b03e07d673baf63f78c':'1705589966,1706282698,1706374969'
}

sign = "759c46ed8f8b67c3a9a82b8c0d3d34f6ab074ce60bc57f9e24d55f26f2c897ae0713afa2939bf930cc0d8266b7b90b08f2538de9925fdd2f883ff10bfa4d335d"

key = 'abcdefgabcdefg12'




def dubbing_for_long(long_text,result_filename,voice_type='male',content_type = 8):
    """
    content_type = 8 为短片，0为长篇
    :param long_text:
    :param result_filename:
    :param voice_type:
    :param content_type:
    :return:
    """
    ## 男生voice_type = 301068 style_degree= 2 pitch=10%
    ## 女生voice_tyoe = 309102 stype_degree= 0 pitch = 0%

    malevoice = {'voice_type':'301068','style_degree': '2','pitch':'10%'}
    femailvoice = {'voice_type':'309102','style_degree': '0','pitch':'0%'}

    if content_type == 8:
        audio_dir = config.audio_directory_short
    elif content_type == 0:
        audio_dir = config.audio_directory_long

    if voice_type == 'female':
        voice = femailvoice
    else:
        voice = malevoice

    get_taskid_url = "https://www.douge.club/peiyin/user/webNewSynGenerateVoiceNew"
    get_data_url = 'https://www.douge.club/peiyin/user/getVoiceAudioUrlWeb'

    payload_get_taskid = '{"speed":16,"text":"'+long_text+'","voice":"'+voice.get('voice_type')+'","styleDegree":'+voice.get('style_degree')+',"pitch":"'+voice.get('pitch')+'","version":"28.0","sign":"'+sign+'"}'
    payload_get_taskid = payload_get_taskid.encode('UTF-8')
    response = requests.request("POST", get_taskid_url, headers=headers, data=payload_get_taskid)
    if response.status_code == 200:
        taskId = json.loads(response.content.decode('UTF-8'))['data']
        print(taskId)
    else:
        return 0
    payload_get_data = '{"taskId":"'+taskId+'"}'
    payload_get_data = payload_get_data.encode('UTF-8')
    time.sleep(20)
    response = requests.request("POST", get_data_url, headers=headers, data=payload_get_data)
    if response.status_code == 200:
        data = json.loads(response.content.decode('UTF-8'))['data']
        print(data)
    cipher = AES.new(key.encode('UTF-8'),mode=AES.MODE_ECB)
    audio_url = cipher.decrypt(base64.b64decode(data))
    response = requests.get(url=audio_url,headers=headers)
    if response.status_code == 200:

        with open(audio_dir+result_filename + '.mp3', 'wb') as file:
            file.write(response.content)
        print(f'音乐文件已成功下载到: {result_filename}')
        return 1
    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 0
        # 以二进制写模式打开文件，并将响应内容写入文件




def dubbing_test(text, voice_type,result_filename):
    """
    转换音频
    :param text:
    :param voice_type:
    :param result_filename:
    :return:
    """
    # 转换语音最多8000字
    url = "https://www.douge.club/peiyin/user/webAudition"
    payload = '{"speed":20,"styleDegree":0,"highDensity":0,"text":"' + text + '","voice":"' + voice_type + '","pitch":"0","sign":"'+sign+'"}'
    payload = payload.encode('UTF-8')
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.content)
        # 以二进制写模式打开文件，并将响应内容写入文件
        with open(video_directory+result_filename+'.mp3', 'wb') as file:
            file.write(response.content)
        print(f'音乐文件已成功下载到: {result_filename}')
        return 1
    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 0



if __name__ == '__main__':
    pass


