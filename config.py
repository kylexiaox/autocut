'''
coding:utf-8
@FileName:config
@Time:2024/2/18 1:44 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''

import time

audio_directory_long = "/Volumes/公共空间/小说推文/配音文件/长片"
audio_directory_short = "/Volumes/公共空间/小说推文/配音文件/短片"
target_directory = "/Volumes/公共空间/解压视频"
video_directory = "/Volumes/公共空间/小说推文/配音文件/短片"
result_directory = "/Volumes/公共空间/小说推文/产出视频/成片/" + time.strftime("%Y-%m-%d", time.localtime())
bgm_directory = "/Volumes/公共空间/小说推文/BGM素材/"


cookies = {
    "kol_fanqie" : "n_mh=iY4X6u7l6MlRNo51VeHduV1Y0ma-JlIjJ0l81ei6IBA; store-region=cn-sh; store-region-src=uid; d_ticket=ce5993f0c541eb0b6af2e4f8d220a6da48599; ttwid=1%7CJEz5kjpZOJDvg3JhVOGnEV107VTNugJzNX0mlfKUJRU%7C1714931727%7C0ece76b799db50efb444270e363a19e712995246b1eb891c4bd9a7607796c8e7; s_v_web_id=verify_lvzghp82_ImANs182_P2hF_4fC5_824E_fUi3YJ6QYF56; msToken=j904jRZy1vz3xNKUZ2m5sPsddayluksILKZ0JiMQLP-I17tgvCP9iUdjPXws8qVvCBF6S_A3jKwSdc4rfXpKLHcbHkoUUPAPsb1p_3oV4YGLDgRv5gJg2ujIe3yMVTQ=; passport_csrf_token=f0f0863074b8fbae4b89fc4a9f6493ef; passport_csrf_token_default=f0f0863074b8fbae4b89fc4a9f6493ef; tt_scid=NfspgjuAHQmMyvsatYLOOiuHNJ0yOwgqpdXI2Uclkxv65fYmhXN3Y-TfhP4IYaH6f52d; odin_tt=7dc0f0ce9f12a4b23acc088dae94c72998bee6264874e225f868bf264754cff357476eaac1a6ca3c679c256d9545561905ba855463d7bbf5620a91743a6bc7cf; passport_auth_status=1ecd718170a6501be61234ccf6c8468d%2C; passport_auth_status_ss=1ecd718170a6501be61234ccf6c8468d%2C; sid_guard=70d3a16299c2f417320f2c6edbdd9c6a%7C1715271748%7C5183999%7CMon%2C+08-Jul-2024+16%3A22%3A27+GMT; uid_tt=7582de8723554ec088e94a6d8f017e87; uid_tt_ss=7582de8723554ec088e94a6d8f017e87; sid_tt=70d3a16299c2f417320f2c6edbdd9c6a; sessionid=70d3a16299c2f417320f2c6edbdd9c6a; sessionid_ss=70d3a16299c2f417320f2c6edbdd9c6a; sid_ucp_v1=1.0.0-KGE3NGFkMmE3YTMxOGI3MDc2MGE2ODJhYzkyZmQyNzg4MzdjMDRkMDUKIAigitDb3s2YBRDE8POxBhjj9xsgDDCZ7_qmBjgCQPEHGgJobCIgNzBkM2ExNjI5OWMyZjQxNzMyMGYyYzZlZGJkZDljNmE; ssid_ucp_v1=1.0.0-KGE3NGFkMmE3YTMxOGI3MDc2MGE2ODJhYzkyZmQyNzg4MzdjMDRkMDUKIAigitDb3s2YBRDE8POxBhjj9xsgDDCZ7_qmBjgCQPEHGgJobCIgNzBkM2ExNjI5OWMyZjQxNzMyMGYyYzZlZGJkZDljNmE; msToken=iZ_DmRs4GXZdvLO73U55bOzthrhFBNOU7yYoOkBI3uygjuPJJOGA3kYp7wdh_7NsUclWy51RyLWAdIHNeoHRfXTTIdL6K4G_Si1vYcrLe1yZHARf_z6DGnxFzDpt7xY="}

label_str = {
    # 'fanqie' : '番茄小说sou:'
    'fanqie' : '# '
}

title_str = {
    'fanqie' : '🍅小说sou:'
}

icon_file = {
    'fanqie' :  'fanqie.png'
}

font ={
    '字魂劲道黑':'/Users/xiangxiao/Documents/Fonts/字魂劲道黑.ttf',
    '字魂大黑':'/Users/xiangxiao/Documents/Fonts/字魂大黑-SemiBold.ttf',
    '字小魂萌趣欢乐体':'/Users/xiangxiao/Documents/Fonts/字小魂萌趣欢乐体.ttf',
    '字小魂霓虹体':'/Users/xiangxiao/Documents/Fonts/字小魂霓虹体(商用需授权).ttf',
    '字魂镇魂手书':'/Users/xiangxiao/Documents/Fonts/字魂镇魂手书.ttf',
}

cover_img = {
    'girl1': '/Volumes/公共空间/小说推文/封面素材/girl1.png',
    'girl2': '/Volumes/公共空间/小说推文/封面素材/girl2.png',
    'girl3': '/Volumes/公共空间/小说推文/封面素材/girl3.png',
    'girl4': '/Volumes/公共空间/小说推文/封面素材/girl4.png',
    'girl1_large': '/Volumes/公共空间/小说推文/封面素材/girl1_large.png',
    'girl2_large': '/Volumes/公共空间/小说推文/封面素材/girl2_large.png',
    'girl3_large': '/Volumes/公共空间/小说推文/封面素材/girl3_large.png',
    'girl4_large': '/Volumes/公共空间/小说推文/封面素材/girl4_large.png',

}

# 账户id

account = {
    'douyin_nv1':{
        'account_id':34663015465,
        'cover_img':'girl1_large',
        'voice_type':'female',
        'video_type':'迷你厨房'
    },
    'douyin_nan1':{
        'account_id': 47040731565,
        'cover_img':'girl2_large',
        'voice_type':'male',
        'video_type':'蛋仔素材'
    }
}


# 数据库参数
DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '1qaz@WSX',
        'database': 'douyin',
        'charset': 'utf8'
    }
DB_NAME = {
        'video_record':'video_record'
}

video_setting = {

    '迷你厨房': {
        'path': '迷你厨房',
        'label': {
            'font':font.get('字魂大黑'),
            'font_size': 10,
            'color': 'black',
            'stroke_color': 'white',
            'stroke_width': 2,
            'size': (300, None),
            'pic_size': (60,60),
            'txt_position': ('center', 300),
            'pic_position': ('center', 200)
        },
        'srt': {
            'font': font.get('字小魂萌趣欢乐体'),
            'font_size': 35,
            'color': 'white',
            'stroke_color': 'black',
            'stroke_width': 1,
            'size': (450, None),
            'srt_position': ('center', 570)
        },
        'bitrate': '3000k',
        'frag_dur': 30,
        'speed': 1,
        'width': None,
        'length': None,
        'new_resolution':None,
    },

    '蛋仔素材': {
        'path': '/蛋仔素材/2023年 6月-12月更新/竞速图',
        'label': {
            'font':font.get('字魂大黑'),
            'font_size': 70,
            'color': 'white',
            'stroke_color':'black',
            'stroke_width':2,
            'size':(300, None),
            'pic_size':(60,60),
            'txt_position':('center', 250),
            'pic_position':('center', 150)
        },
        'srt': {
            'font': font.get('字魂劲道黑'),
            'font_size': 40,
            'color': 'black',
            'stroke_color': 'white',
            'stroke_width': 2,
            'size': (900, None),
            'srt_position': ('center', 800)
        },
        'bitrate': '3000k',
        'frag_dur': 30,
        'speed': 1,
        'width': 1280,
        'length': None,
        'new_resolution':(720,1280)

    }
}

## bgm 音量
bgm_volume = {
    'default': 0.15,
    "用情": 0.13
}