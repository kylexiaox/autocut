'''
coding:utf-8
@FileName:assembler
@Time:2024/1/20 7:11 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''
import re
import string
import sys
import os
# 将外层目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import *
import time
import threading
import logger
from .utils import *
from crawler.fanqie_crawler import fanqie_crawler
from crawler.dub import *
from .video_autocut import *
from moviepy.audio.fx.volumex import volumex
from moviepy.video.tools.subtitles import SubtitlesClip
import pysrt
from PIL import Image
import redis
from functools import wraps
import time
from factory import dao




def retry(max_retries=3, delay=1):
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


def log_progress(stop_event,taskid):
    """
    记录视频处理进度
    :param stop_event:
    :return:
    """
    while not stop_event.is_set():
        logger.assemble_logger.info("Video processing in progress...")
        message_dict = {'taskid': taskid, 'message': f'输出视频...'}
        logger.ws_logger.info(json.dumps(message_dict))
        stop_event.wait(15)  # 每隔 15 秒记录一次日志


def assembler(bookid, bgm_name, alias, publish_time, account, content_type=0, voice_type='female',
              video_type='西餐美食小吃视频', platform='fanqie',
              bitrate='5000k', cover_img='girl1_large',is_summary=True, is_test=False):
    """
    视频混剪函数，
    :param bookid:
    :param bgm_name:
    :param alias:
    :param publish_time:
    :param account:
    :param content_type:
    :param voice_type:
    :param video_type:
    :param platform:
    :param bitrate:
    :param cover_img:
    :param is_test:
    :return:
    """
    # 获取内容音频
    taskid = str(account) + str(bookid)
    fq_crawler = fanqie_crawler()
    message_dict = { 'taskid': taskid, 'message': f'开始获取内容和音频...' }
    logger.ws_logger.info(json.dumps(message_dict))
    audio_clip, srt_path, book_name = get_text_voice(fq_crawler, bookid, content_type=content_type,
                                                     voice_type=voice_type, use_cache=True,is_summary=is_summary, is_test=is_test)
    # 音量标准化
    message_dict = {'taskid': taskid, 'message': f'处理音频+BGM...'}
    logger.ws_logger.info(json.dumps(message_dict))
    audio_clip = audio_clip.audio_normalize()
    video_len = audio_clip.duration
    logger.assemble_logger.info(f'处理BGM,BGM使用的是{bgm_name}')
    bgm_clip = AudioFileClip(config.bgm_directory + bgm_name + '/head.MP3').audio_normalize()
    bgm_tail_clip = AudioFileClip(config.bgm_directory + bgm_name + '/tail.MP3').audio_normalize()
    if video_len > bgm_clip.duration:
        tmp_bgm_clip = afx.audio_loop(bgm_tail_clip, duration=(video_len - bgm_clip.duration))
        bgm_clip = concatenate_audioclips([bgm_clip, tmp_bgm_clip])
    else:
        bgm_clip = bgm_clip.subclip(t_start=0, t_end=video_len)
    if config.bgm_volume.get(bgm_name) is not None:
        bgm_volume = config.bgm_volume.get(bgm_name)
    else:
        bgm_volume = config.bgm_volume.get('default')
    bgm_clip = bgm_clip.fx(volumex, bgm_volume)
    logger.assemble_logger.info(f'处理音频，合并BGM和内容音频')
    overlay_audio_clip = CompositeAudioClip([audio_clip, bgm_clip])
    overlay_audio_clip.fps = 44100
    logger.assemble_logger.info(f'合并解压视频素材')
    message_dict = {'taskid': taskid, 'message': f'合并素材...'}
    logger.ws_logger.info(json.dumps(message_dict))
    video_clip, filelog = combineVideo(tim_len=overlay_audio_clip.duration, frag_dur=None, speed=1,
                                       video_type=video_type,
                                       write=False)
    logger.assemble_logger.info(f'音视频合并')
    message_dict = {'taskid': taskid, 'message': f'音视频合并...'}
    logger.ws_logger.info(json.dumps(message_dict))
    video_clip = video_clip.set_audio(overlay_audio_clip)
    # 创建字幕文本剪辑
    logger.assemble_logger.info('处理字幕')
    message_dict = {'taskid': taskid, 'message': f'处理字幕...'}
    logger.ws_logger.info(json.dumps(message_dict))
    video_clip = add_srt_to_video(srt_file=srt_path, video_clip=video_clip, video_type=video_type)
    logger.assemble_logger.info('处理标题别名')
    message_dict = {'taskid': taskid, 'message': f'处理标题别名...'}
    logger.ws_logger.info(json.dumps(message_dict))
    # label_text = config.label_str.get('fanqie') + '\n《' + alias + '》'
    label_text = config.label_str.get(platform) + alias
    final_clip = add_label_to_video(text=label_text, pic_file=config.icon_file.get(platform), video_clip=video_clip,
                                    video_type=video_type)
    if is_test:
        output_folder = config.result_directory + '/' + 'test_' + str(bookid) + '_' + book_name
    else:
        output_folder = config.result_directory + '/' + str(bookid) + '_' + book_name
    c_time = str(time.time()).split('.')[0]
    output_path = os.path.join(output_folder, str(bookid) + '_' + bgm_name + '.mp4')
    # 确保输出文件夹路径存在，如果不存在则创建
    logger.assemble_logger.info('处理简介摘要')
    message_dict = {'taskid': taskid, 'message': f'处理简介摘要...'}
    logger.ws_logger.info(json.dumps(message_dict))
    with open(output_folder + '/' + book_name + '_original_text.txt', 'r') as file:
        # 读取文件内容
        description = file.read()
        description = get_text_before_dot(description, count=4)
    logger.assemble_logger.info('处理title')
    title_str = config.title_str.get(platform) + '《' + alias + '》'
    logger.assemble_logger.info('输出目录为 : ' + output_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(os.path.join(output_folder, c_time + '_' + str(bookid) + '_log.txt'), 'w') as file:
        file.write(filelog)
    fps = final_clip.fps
    # 导出视频
    stop_event = threading.Event()
    threading.Thread(target=log_progress, args=(stop_event,taskid)).start()
    try:
        message_dict = {'taskid': taskid, 'message': f'输出视频...'}
        logger.ws_logger.info(json.dumps(message_dict))
        final_clip.write_videofile(output_path, codec='h264_videotoolbox', bitrate=bitrate, fps=fps,
                               preset='slow')
    except Exception as e:
        logger.assemble_logger.error(f'视频导出失败，错误信息：{e}', exc_info=True)
        raise e
    finally:
        stop_event.set()
    # medium
    logger.assemble_logger.info('视频文件写入完成')
    logger.assemble_logger.info("处理封面")
    get_cover_img(text=f"《{alias}》", w_l_ratio=final_clip.size[0] / final_clip.size[1], img=cover_img,
                  output_folder=output_folder)
    # push_to_media(account='account',filepath=output_folder,title=f"番茄小说sou：《{alias}》",publish_time= publish_time)
    result = {'book_id': bookid, 'alias': alias, 'book_name': book_name, 'account': account, 'filepath': output_folder,'title': title_str,
                'description': description,
                'publish_time': publish_time, 'content_type': 'short_novel'}
    logger.assemble_logger.info(f'处理完成，返回结果：{result}')
    return result


def get_text_voice(crawler, bookid, content_type=0, voice_type='female', use_cache=True, is_summary=True, is_test=False):
    """
    通过bookid拿音频+字幕
    :param bookid:
    :param content_type:
    :param voice_type:
    :param use_cache: false 重新请求，true，不重新请求
    :param is_test: 返回测试内容，100个字
    :return:
    """
    if content_type == 0:
        # 短篇
        bookinfo = crawler.get_book_info(bookid)
        if is_test:
            # 测试环境的文件夹
            final_output_folder = config.result_directory + '/' + 'test_' + str(bookid) + '_' + bookinfo[0]
        else:
            final_output_folder = config.result_directory + '/' + str(bookid) + '_' + bookinfo[0]
        if use_cache is True and os.path.exists(final_output_folder + '/' + bookinfo[0] + '.mp3'):
            # 如果文件存在，直接返回存量的内容
            srt_path = final_output_folder + '/' + bookinfo[0] + '.srt'
            audio_clip = AudioFileClip(final_output_folder + '/' + bookinfo[0] + '.mp3')
            return audio_clip, srt_path, bookinfo[0]
        logger.assemble_logger.info(f"获取音频文件：{bookid}")
        bookinfo = crawler.get_book_info(bookid)
        origin_summary,origin_content = crawler.get_content_from_fanqie_dp(bookid,is_summary)
        logger.assemble_logger.info(f"origin_summary:{origin_summary}")
        logger.assemble_logger.info(f"origin_content:{origin_content[:100]}")
        if origin_summary != '' and origin_summary is not None:
            cleaned_summary = clean_the_text(origin_summary)
        cleaned_text = clean_the_text(origin_content) # 去除第一章、1,等内容
        if is_test:
            # 测试环境中只保留100字
            cleaned_text = cleaned_text[:100]

        texts = split_content(cleaned_text, gap=6000, end_with='。')
        paths = []
        for index, text in enumerate(texts):
            paths.append(dubbing_for_long(long_text=text, result_filename=str(bookinfo[0]) + '_' + str(index),
                                          voice_type=voice_type,
                                          output_dir=config.result_directory + '/' + str(bookid) + '_' + bookinfo[0],
                                          use_cache=use_cache))
        info_str = 'book_id : ' + str(bookinfo[2]) + '\n'
        info_str += 'book_name : ' + bookinfo[0] + '\n'
        info_str += 'abstract : ' + bookinfo[1]
        # 获取摘要,和拆分的summary做比对
        if origin_summary != '' and origin_summary is not None:
            abstract = cleaned_summary
        else:
            abstract = bookinfo[0]
        if count_chinese_characters(abstract) < 20:
            # 如果当前摘要小于20个字，得从正文中截取
            abstract = split_content(text, gap=30, end_with='。')[0]
        if not os.path.exists(final_output_folder):
            os.makedirs(final_output_folder)
        with open(config.audio_directory_short + bookinfo[0] + '_info.txt', 'wb') as file:
            file.write(info_str.encode('UTF-8'))
        with open(os.path.join(final_output_folder, bookinfo[0] + '_info.txt'), 'wb') as file:
            file.write(info_str.encode('UTF-8'))
        with open(os.path.join(final_output_folder, bookinfo[0] + '_text.txt'), 'wb') as file:
            file.write(text.encode('UTF-8'))
        with open(os.path.join(final_output_folder, bookinfo[0] + '_original_text.txt'), 'wb') as file:
            file.write(text.encode('UTF-8'))
        with open(config.audio_directory_short + bookinfo[0] + '_text.txt', 'wb') as file:
            file.write(text.encode('UTF-8'))
        with open(os.path.join(final_output_folder, 'abstract.txt'), 'wb') as file:
            file.write(abstract.encode('UTF-8'))
        audio_clip = None
        for path in paths:
            if audio_clip is None:
                audio_clip = AudioFileClip(path[0])
            else:
                audio_clip = concatenate_audioclips([audio_clip, AudioFileClip(path[0])])
        audio_path = final_output_folder + '/' + bookinfo[0] + '.mp3'
        audio_clip.write_audiofile(audio_path)
        srts = []
        for path in paths:
            srts.append(path[1])
        srt_clip = merge_srt(srts)
        srt_path = final_output_folder + '/' + bookinfo[0] + '.srt'
        srt_clip.save(srt_path)
        return audio_clip, srt_path, bookinfo[0]
    else:
        # 长篇
        pass


@retry()
def add_srt_to_video(srt_file, video_clip, video_type):
    srt_config = config.video_setting.get(video_type).get('srt')
    logger.assemble_logger.info(f'添加字幕文件到视频中，字幕文件{srt_file}')
    with open(srt_file, "r") as input_f, open('temp_srt.srt', "w") as output_f:
        lines = input_f.readlines()
        for i in range(0, len(lines), 4):
            index = lines[i]
            time = lines[i + 1]
            content = lines[i + 2]
            # 剔除字幕内容中的标点符号
            content = filter_non_chinese(content)
            # 空串剔除
            if content == '':
                continue
            # 写回到新文件中
            output_f.write(index)
            output_f.write(time)
            output_f.write(content + '\n')
            output_f.write("\n")

    def generate_text(txt):
        # txt = filter_non_chinese(txt)
        return TextClip(txt, font=srt_config.get('font'), fontsize=srt_config.get('font_size'),
                        color=srt_config.get('color'), stroke_color=srt_config.get('stroke_color'),
                        stroke_width=srt_config.get('stroke_width'),
                        method='caption', size=srt_config.get('size'))

    # subtitles = SubtitlesClip.load_subtitles('temp_srt.srt')
    # subtitles = subtitles.set_text_generator(generate_text)
    subtitles = SubtitlesClip('temp_srt.srt', generate_text)
    result = CompositeVideoClip([video_clip, subtitles.set_position(srt_config.get('srt_position'), relative=False)])
    # 删除temp srt内容
    os.remove('temp_srt.srt')
    # 输出结果视
    # result.write_videofile("output.mp4",fps=video_clip.fps)
    return result


@retry()
def add_label_to_video(text, pic_file, video_clip, video_type):
    # 拿配置
    label_config = config.video_setting.get(video_type).get('label')
    text_clip = TextClip(text, font=label_config.get('font'), fontsize=label_config.get('font_size'),
                         color=label_config.get('color'), stroke_color=label_config.get('stroke_color'),
                         stroke_width=label_config.get('stroke_width'), size=label_config.get('size'))
    text_clip = text_clip.set_position(label_config.get('txt_position'))
    text_clip = text_clip.set_duration(video_clip.duration)
    if pic_file:
        pic_img = Image.open(pic_file)
        pic_img = pic_img.resize(size=label_config.get('pic_size'))
        pic_img.save('temp_pic.png')
        pic_clip = ImageClip('temp_pic.png')
        pic_clip = pic_clip.set_duration(video_clip.duration)
        pic_clip = pic_clip.set_position(label_config.get('pic_position'))

    video_with_pic = CompositeVideoClip([video_clip, pic_clip])
    video_with_text = CompositeVideoClip([video_with_pic, text_clip])
    # video_with_text.write_videofile("output.mp4",fps=video_clip.fps)
    return video_with_text


@retry()
def merge_srt(srts):
    """
    合并srt
    :param srts:
    :return:
    """
    end = 0
    for index, srt in enumerate(srts):
        subs = pysrt.open(srt)
        if index == 0:
            temp_subs = subs
            t_end_sub = temp_subs[-1]
            end = t_end_sub.index
            end_time = temp_subs[-1].end
        else:
            for sub in subs:
                sub.index = end + sub.index
                sub.shift(hours=end_time.hours, minutes=end_time.minutes, seconds=end_time.seconds,
                          milliseconds=end_time.milliseconds)
                temp_subs.append(sub)
    return temp_subs


def clean_the_text(text, ) -> string:
    cleaned_text = ''.join([char for char in text if char != '"'])
    cleaned_text = cleaned_text.replace('*','')
    # 使用正则表达式匹配 "第x章" 格式的内容，并将其替换为空字符串
    # cleaned_text = re.sub(r'(?<!第)第(?:[一二三四五六七八九十百千\d]+|[1-9]\d*)章', '', cleaned_text)
    return cleaned_text


def get_cover_img(text, img, output_folder="", w_l_ratio=0.75, font='字魂劲道黑', ):
    # 打开图像文件
    img = Image.open(config.cover_img.get(img))
    # 计算裁剪的区域
    left = math.floor(img.size[0] / 2 - math.floor(img.size[0] * w_l_ratio / 2))
    right = math.floor(img.size[0] / 2 + math.floor(img.size[0] * w_l_ratio / 2))
    top = 0
    bottom = img.size[1]
    # 裁剪图像
    cropped_image = img.crop((left, top, right, bottom))
    cropped_image.save('tmp_cover.png')
    # 创建 ImageClip 对象
    img_clip = ImageClip('tmp_cover.png')
    # 创建文本剪辑
    text_clip = TextClip(txt=text, font=config.font.get(font), fontsize=70, color='white', stroke_color='black',
                         stroke_width=2)
    # 获取文本剪辑的尺寸
    text_width, text_height = text_clip.size
    # 计算文本剪辑的位置，使其居中显示
    text_x = (img_clip.size[0] - text_width) / 2
    text_y = (img_clip.size[1] - text_height) / 2
    # 设置文本剪辑的位置
    text_clip = text_clip.set_position((text_x, text_y))
    # 将文本剪辑合并到背景视频剪辑上
    final_clip = CompositeVideoClip([img_clip, text_clip])
    # 生成合成图像
    final_image_np = final_clip.get_frame(0)  # 获取第 0 秒的图像帧
    final_image_pil = Image.fromarray(final_image_np)
    # 保存合成图像
    final_image_pil.save(output_folder + '/' + "cover.png")


def push_to_media(account, filepath, title, publish_time, img_path=None, type='douyin_short'):
    if img_path is None:
        img_path = filepath + '/' + "cover.png"
    with open(filepath + '/' + 'abstract.txt', 'r') as file:
        # 读取文件内容
        description = file.read()
    url = 'http://127.0.0.1:23335/douyin/' + account
    form = {
        'filepath': filepath,
        'title': title,
        'type': type,
        'description': description,
        'img_path': img_path,
        'publish_time': publish_time
    }
    response = requests.request(method='POST', url=url, data=form, timeout=1500)
    logger.assemble_logger.infologger.assemble_logger.info(response.text)


def push_to_message_queue(book_name, book_id, content_type, alias, account, filepath, title, description, publish_time,
                          img_path=None, type='douyin_short', platform='fanqie'):
    """

    :param book_name: 书名
    :param book_id: 书id
    :param content_type:
    :param alias: 别名
    :param account: 抖音账户
    :param filepath: 文件目录
    :param title: 抖音标题
    :param description: 抖音描述
    :param publish_time:
    :param img_path:
    :param type: 定位到tags
    :param platform:
    :return:
    一个mq的消息包体
    {'book_id': 7348020574980951102, 'alias': '备胎日记', 'book_name': '不当舔狗后', 'account': 47040731565,
     'filepath': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-12/7348020574980951102_不当舔狗后', 'title': '番茄小说sou：《备胎日记》',
     'type': 'douyin_short',
     'description': '在一起的第六年，我跟许钰提了分手。原因是我在她的车上看到了猫毛。而她从来不让我的猫上她的车，她说她有洁癖。听我这么说她无所谓的耸肩：[就因为这个？]因为这个，也不只因为是这个',
     'img_path': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-12/7348020574980951102_不当舔狗后/cover.png', 'platform': 'fanqie',
     'publish_time': '2024-06-01 11:00', 'content_type': 'short_novel'}
    """
    # 连接到 Redis 服务器
    r = redis.StrictRedis(host=REDIS_CONFIG.get('host'), port=REDIS_CONFIG.get('port'), db=REDIS_CONFIG.get('db'))

    # 生成唯一的uuid
    if img_path is None:
        img_path = filepath + '/' + "cover.png"
    form = {
        'book_id': book_id,
        'alias': alias,
        'book_name': book_name,
        'account': account,
        'filepath': filepath,
        'title': title,
        'type': type,
        'description': description,
        'img_path': img_path,
        'platform': platform,
        'publish_time': publish_time,
        'content_type': content_type
    }
    message_id = r.xadd("task_queue", form)
    logger.assemble_logger.info(f"=======发送数据id：{message_id},消息： {form}")


def push_to_mq_test(msg):
    # 连接到 Redis 服务器
    r = redis.StrictRedis(host=REDIS_CONFIG.get('host'), port=REDIS_CONFIG.get('port'), db=REDIS_CONFIG.get('db'))

    message_id = r.xadd("task_queue", msg)
    logger.assemble_logger.info(f"测试发送数据id：{message_id},消息： {msg}")


def video_output(account_name, bookid, publish_time, bgm_name=None, is_test=False,is_push=True,is_summary= True):
    # 封装 消息字符串
    account = config.account.get(account_name).get('account_id')
    # 封装task dict

    taskid = str(account) + str(bookid)
    message_dict = {'taskid': taskid, 'message': f'任务开始处理'}
    logger.ws_logger.info(json.dumps(message_dict))
    if dao.check_dumplicate(book_id=bookid, account_name=account_name):
        logger.assemble_logger.info(f'video task is duplicate return False')
        message_dict = {'taskid': taskid, 'message': f'任务重复，结束处理'}
        logger.ws_logger.info(json.dumps(message_dict))
        raise Exception(message_dict)
    logger.assemble_logger.info(f'开始处理任务：书籍id是：{bookid},发布时间：{publish_time},BGM：{bgm_name},发布到账户：{account_name}上....')
    task = {
        'taskid': taskid,
        'account_name': account_name,
        'book_id': bookid,
        'publish_time': publish_time
    }
    # 把task添加到列表里，并返回index
    task_idx = dao.tasks.push(task)
    logger.assemble_logger.info(f'Task added to queue, index: {task_idx}')
    try:
        if bgm_name is None:
            # 随机分配音乐
            bgm_dir = '/Volumes/公共空间/小说推文/BGM素材/'
            bgms = [f.name for f in os.scandir(bgm_dir) if f.is_dir()]
            bgm_name = random.choice(bgms)
        crawler = fanqie_crawler()
        alias_name, alias_id = crawler.get_alias_id(book_id=bookid)

        voice_type = config.account.get(account_name).get('voice_type')
        cover_img = config.account.get(account_name).get('cover_img')
        video_type = config.account.get(account_name).get('video_type')
        result = assembler(bookid=bookid, bgm_name=bgm_name, voice_type=voice_type, account=account, video_type=video_type,
                          cover_img=cover_img, publish_time=publish_time, alias=alias_name,is_summary = is_summary, is_test=is_test)
        # result = {'book_id': '7366551041162103833', 'alias': '打脸男闺蜜', 'book_name': '感化不了的妻子，我不要了', 'account': 30365867345, 'filepath': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-26/7366551041162103833_感化不了的妻子，我不要了', 'title': '🍅小说sou:《打脸男闺蜜》', 'description': '杀青庆功宴上，老婆把赞助商送的男款情侣表送给了前男友。二人拿着情侣表拍了张接吻照。大伙儿看了我一眼错愕的问她：“沈老师，你亲错人了吧？”“戏都拍完了，这是什么情况', 'publish_time': '0', 'content_type': 'short_novel'}
        if is_push:
            push_to_message_queue(book_name=result.get('book_name'), book_id=result.get('book_id'),
                                  content_type=result.get('content_type'), alias=result.get('alias'),
                                  account=result.get('account'), filepath=result.get('filepath'), title=result.get('title'),
                                  description=result.get('description'), publish_time=result.get('publish_time'),
                                  img_path=result.get('img_path'),)
            return result
        else:
            logger.assemble_logger.info(f'测试环境，不推送到消息队列')
            return result
    except Exception as e:
        logger.assemble_logger.error(f'视频处理失败，错误信息：{e}', exc_info=True)
        message_dict = {'taskid': taskid, 'message': f'任务处理失败，错误信息：{e}'}
        logger.ws_logger.info(json.dumps(message_dict))
        raise e
    finally:
        dao.tasks.pop(task_idx)
        logger.assemble_logger.info(f'Task removed from queue, index: {task_idx}')




if __name__ == '__main__':
    pass
    push_to_mq_test({'book_id': 7348020574980951102, 'alias': '备胎日记', 'book_name': '不当舔狗后', 'account': 47040731565,
     'filepath': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-12/7348020574980951102_不当舔狗后', 'title': '番茄小说sou：《备胎日记》',
     'type': 'douyin_short',
     'description': '在一起的第六年，我跟许钰提了分手。原因是我在她的车上看到了猫毛。而她从来不让我的猫上她的车，她说她有洁癖。听我这么说她无所谓的耸肩：[就因为这个？]因为这个，也不只因为是这个',
     'img_path': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-12/7348020574980951102_不当舔狗后/cover.png', 'platform': 'fanqie',
     'publish_time': '2024-06-01 11:00', 'content_type': 'short_novel'})

    # video_output(account_name='douyin_nan1', bookid=7348020574980951102, bgm_name='用情',
    #              publish_time='2024-05-14 11:00')
    # video_output(account_name='douyin_nan1', bookid=7355507776015043646, bgm_name='凄美地',
    #              publish_time='2024-05-14 18:00')
    # video_output(account_name='douyin_nan1', bookid=7351733248306711614, bgm_name='富士山下',
    #              publish_time='2024-05-12 10:00')
    # video_output(account_name='douyin_nan1', bookid=7133640097534053406, bgm_name='暖一杯茶',
    #              publish_time='2024-05-12 15:00')
    # video_output(account_name='douyin_nan1', bookid=7282959964250112575, bgm_name='兰亭序',
    #              publish_time='2024-05-13 11:00')
    # video_output(account_name='douyin_nan1', bookid=7223704892630633532, bgm_name='冬眠',
    #              publish_time='2024-05-13 18:00',is_test=True)

    # video_output(account_name='douyin_nv1', bookid=7299355308596399145,
    #              publish_time='2024-05-13 11:00',)
    # video_output(account_name='douyin_nv1', bookid=7314580388494445604,
    #              publish_time='2024-05-13 18:00',)
    # video_output(account_name='douyin_nv1', bookid=7322348136427424830,
    #              publish_time='2024-05-14 11:00',)

    # video_output(account_name='douyin_nv1', bookid=7301877628695219240,
    #              publish_time='2024-05-14 18:00', bgm_name='暖一杯茶')
    # video_output(account_name='douyin_nv1', bookid=7264865084881505314,
    #              publish_time='2024-05-15 11:00')
    # video_output(account_name='douyin_nv1', bookid=7348385435980153406,
    #              publish_time='2024-05-16 12:00')

        # video_output(account_name='douyin_nv1', bookid=7369200831616254526, bgm_name='富士山下',
        #              publish_time=None)
        # video_output(account_name='douyin_nan1', bookid=7366551041162103833, bgm_name='我离开了南京',
        #             publish_time='0')
    # video_output(account_name='douyin_nan1', bookid=7330837915712359486,bgm_name='赤伶',
    #           publish_time=None)
    # video_output(account_name='douyin_nan1', bookid=7333102653397814334,bgm_name='凄美地',
    #              publish_time='2024-05-25 11:00')
    # video_output(account_name='douyin_nv1', bookid=7133640097534053406,bgm_name='悬溺',
    #              publish_time='2024-05-24 11:00')
    # video_output(account_name='douyin_nan1', bookid=7330837915712359486,bgm_name='赤伶',
    #              publish_time='2024-05-23 11:30')

    # assembler(bookid=7355507776015043646, bgm_name='凄美地', voice_type='male', video_type='蛋仔素材',
    #           alias=crawler.ge, publish_time='2024-05-12 10:00', account=config.account.get('douyin_nan1'),
    #           cover_img='girl1_large')
    # assembler(bookid=7282959964250112575, bgm_name='用情', voice_type='male', video_type='蛋仔素材',
    #           alias='阿恒日记', publish_time='2024-05-06 19:00',account=config.account.get('douyin_nan1'))
