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
import os

import requests
from text import *
import json
from Crypto.Cipher import AES
import base64
import time
import config


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Access-Token': '3217169178521598',
    'Content-Type': 'application/json;charset=UTF-8',
    "Cookie": "shareToken=3217169178521598",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.douge.club/",
}

### 重新登陆 主要是换 头里的 X-A-token
cookies = {
    'Hm_lvt_f5b437a514220b03e07d673baf63f78c': '1710257168,1711811849',
    'fromId': 'bdmyzirj',
    'shareToken': '3217169178521598',
    'Hm_lpvt_f5b437a514220b03e07d673baf63f78c':'1711812689'

}

sign = "6e4739abf14a3fa5c2fa41e6da89e5cb12a3a0f9e2e4c9846c1454627345678260829eb18b0b2070c70b7a9ae19024416c84ce91045af90c7ddbd0f7e0cca2dd"

key = 'abcdefgabcdefg12'




def dubbing_for_long(long_text,result_filename,voice_type='male',content_type = 8,output_dir = None,flag = False,srt = False):
    """
    content_type = 8 为短片，0为长篇
    flag  为存量拉取
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

    if output_dir is None:
        if content_type == 8:
            output_dir = config.audio_directory_short
        elif content_type == 0:
            output_dir = config.audio_directory_long

    if flag is True:
        return output_dir + '/' +result_filename + '.mp3',output_dir+'/' +result_filename+'.srt'


    if voice_type == 'female':
        voice = femailvoice
    else:
        voice = malevoice

    get_taskid_url = "https://www.douge.club/peiyin/user/webNewSynGenerateVoiceNew"
    get_data_url = 'https://www.douge.club/peiyin/user/getVoiceAudioUrlWeb'
    get_srt_id_url = 'https://www.douge.club/peiyin/user/analyzeAudioUrlWeb'
    get_srt_url = 'https://www.douge.club/peiyin/user/analyzeResultWeb'

    payload_get_taskid = '{"speed":16,"text":"'+long_text+'","voice":"'+voice.get('voice_type')+'","styleDegree":'+voice.get('style_degree')+',"pitch":"'+voice.get('pitch')+'","version":"28.0","sign":"'+sign+'"}'

    payload_get_taskid = payload_get_taskid.encode('UTF-8')
    response = requests.request("POST", get_taskid_url, headers=headers, data=payload_get_taskid)
    if response.status_code == 200:
        print(response.content.decode('UTF-8'))
        taskId = json.loads(response.content.decode('UTF-8'))['data']
        print(taskId)
    else:
        return 0
    payload_get_data = '{"taskId":"'+taskId+'"}'
    payload_get_data = payload_get_data.encode('UTF-8')
    time.sleep(120)
    response = requests.request("POST", get_data_url, headers=headers, data=payload_get_data)
    if response.status_code == 200:
        data = json.loads(response.content.decode('UTF-8'))['data']
        print(data)
    cipher = AES.new(key.encode('UTF-8'),mode=AES.MODE_ECB)
    audio_url = cipher.decrypt(base64.b64decode(data))
    response = requests.get(url=audio_url,headers=headers)
    if response.status_code == 200:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        audio_path = output_dir + '/' +result_filename + '.mp3'
        with open(audio_path, 'wb') as file:
            file.write(response.content)
        print(f'音乐文件已成功下载到: {result_filename}')

    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 0
    #### 获取字幕
    ## 先拿 taskid
    payload_srt_id = '{"openConfiguration":null,"upUrl":"'+str(audio_url)+'",'+'"text":"'+long_text+'"}'
    payload_srt_id = payload_srt_id.encode('UTF-8')
    response = requests.request("POST",url=get_srt_id_url,headers=headers,data=payload_srt_id)
    if response.status_code ==200:
        srt_taskid = json.loads(response.content.decode('UTF-8'))['data']
    ## 再拿字幕，需要循环
    payload_srt = '{"taskId":"'+srt_taskid+'","web":true,"textLength":null,"openConfiguration":null,"leaveBlank":true}'
    counter = 0
    while(counter<20):
        response = requests.request(method='POST',url=get_srt_url,data=payload_srt,headers=headers)
        if response.status_code == 200:
            print(response.content.decode('UTF-8'))
            data = json.loads(response.content.decode('UTF-8'))['data']
            if data['status'] == 1:
                srt_downlaod_url = data['srtUrl']
                srt_response = requests.get(srt_downlaod_url)
                srt_path = output_dir+'/' +result_filename+'.srt'
                with open(srt_path, 'wb') as file:
                    file.write(srt_response.content)
                print(f"文件 '{result_filename+'.srt'}' 下载成功！")
                break
            else:
                counter += 1
                time.sleep(2)
                continue
    return audio_path,srt_path





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
        with open(config.video_directory+result_filename+'.mp3', 'wb') as file:
            file.write(response.content)
        print(f'音乐文件已成功下载到: {result_filename}')
        return 1
    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 0



if __name__ == '__main__':
    pass


