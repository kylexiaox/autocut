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


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Access-Token': '5528714820020229',
    'Content-Type': 'application/json;charset=UTF-8',
    "Cookie": "shareToken=9111111113018116",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.douge.club/",
}

cookies = {
    'Hm_lvt_f5b437a514220b03e07d673baf63f78c': '1705589966',
    'fromId': 'bdbrand',
    'shareToken': '5528714820020229',
    'Hm_lpvt_f5b437a514220b03e07d673baf63f78c': '1705590163'
}

sign = "fe72b4e8b57e1c6523599d57143b39f74544d353af51b645673b7a54c96ad028d77acf89af2df9d693d39715995df59a7d972d7866926f17f30104f6130ada5b"

key = 'abcdefgabcdefg12'

def dubbing_for_long(long_text,result_filename,voice_type=301068,):
    """
    长文本=>音频
    :param long_text:
    :param voice_type:
    :param result_filename:
    :return:
    """

    get_taskid_url = "https://www.douge.club/peiyin/user/webNewSynGenerateVoiceNew"
    get_data_url = 'https://www.douge.club/peiyin/user/getVoiceAudioUrlWeb'

    payload_get_taskid = '{"speed":15,"text":"'+long_text+'","voice":"'+str(voice_type)+'","styleDegree":2,"pitch":"10%","version":"28.0","sign":"'+sign+'"}'
    payload_get_taskid = payload_get_taskid.encode('UTF-8')
    response = requests.request("POST", get_taskid_url, headers=headers, data=payload_get_taskid)
    if response.status_code == 200:
        taskId = json.loads(response.content.decode('UTF-8'))['data']
        print(taskId)
    else:
        return 0
    payload_get_data = '{"taskId":"'+taskId+'"}'
    payload_get_data = payload_get_data.encode('UTF-8')
    response = requests.request("POST", get_data_url, headers=headers, data=payload_get_data)
    if response.status_code == 200:
        data = json.loads(response.content.decode('UTF-8'))['data']
        print(data)
    cipher = AES.new(key.encode('UTF-8'),mode=AES.MODE_ECB)
    audio_url = cipher.decrypt(base64.b64decode(data))
    response = requests.get(url=audio_url,headers=headers)
    if response.status_code == 200:
        print(response.content)
        with open(result_filename + '.mp3', 'wb') as file:
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
    payload = '{"speed":5,"styleDegree":0,"highDensity":0,"text":"' + text + '","voice":"' + voice_type + '","pitch":"0","sign":"'+sign+'"}'
    payload = payload.encode('UTF-8')
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.content)
        # 以二进制写模式打开文件，并将响应内容写入文件
        with open(result_filename+'.mp3', 'wb') as file:
            file.write(response.content)
        print(f'音乐文件已成功下载到: {result_filename}')
        return 1
    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 0



if __name__ == '__main__':
    dubbing_for_long('一天已经渐渐变得黑暗，我站在巨大的别墅外。别墅内灯火通明，透过窗户可以隐约看到许家的爸爸妈妈、许白薇和许阳。他们是一个幸福的四口之家，而我却是一个格格不入的外来者。这一切要追溯到三年前，我的养父母去世前告诉我，我是被他们偷换的孩子。为了让他们的亲生儿子过上富裕的生活，他们替我与一个富商家的孩子进行了置换。然而，十几年后，他们意识到错误，感到非常抱歉，并希望我能在他们去世后回到亲生父母身边，找到一个照顾我的人。','重生后')



