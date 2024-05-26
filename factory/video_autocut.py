'''
coding:utf-8
@FileName:assembler
@Time:2024/1/20 7:11 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
这个文件专门处理解压视频的合并
'''

import multiprocessing
from datetime import datetime
from tqdm import tqdm
from multiprocessing import Pool, Process
from concurrent.futures import ProcessPoolExecutor
from moviepy.editor import *
import math
import os
import random
import time
import config
import logger
from moviepy.video.fx.all import *


# 指定要构建目录树的目录


# 进度条装饰器
def progress_bar_decorator(total_iterations, desc="Progress", ncols=100):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 创建进度条
            with tqdm(total=total_iterations, desc=desc, ncols=ncols) as pbar:
                # 执行函数，并传递进度条对象
                result = func(*args, **kwargs, pbar=pbar)
            return result

        return wrapper

    return decorator


def singleton(cls, *args, **kwargs):
    """单例方法"""
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


def build_directory_tree(directory):
    tree = {}
    for root, dirs, files in os.walk(directory):
        current_level = tree
        path = os.path.relpath(root, directory)
        path_parts = path.split(os.path.sep)

        for part in path_parts:
            current_level = current_level.setdefault(part, {})

        for file in files:
            if file.startswith('._'):
                continue
            current_level[file] = None
    return tree


class FileTree:
    def __init__(self, directory):
        self.__file_tree = build_directory_tree(directory)
        self.__file_list = self.__get_video_file_list(self.__file_tree, '')

    def __get_video_file_list(self, tree, context):
        result = []
        for key, value in tree.items():
            if value is None:
                if key.endswith('.mp4'):
                    result.append(context + '/' + key)
            else:
                if key != '.':
                    result = result + self.__get_video_file_list(value, context + '/' + key)
                else:
                    result = result + self.__get_video_file_list(value, context)
        return result

    def get_tree(self):
        return self.__file_tree

    def get_file_list(self):
        return self.__file_list


def sub_clip(clip, frag_dur, ):
    """
    随机选取视频里的内容进行填充
    :param clip:
    :param frag_dur:
    :return:
    """
    d = math.floor(clip.duration / frag_dur)
    if d < 1:
        return clip, 0, d
    else:
        if d <= 2:
            r = 0  # 取中间
        else:
            random.seed(time.time())
            r = random.randint(0, d - 1)
        # 掐头去尾
        clip = clip.subclip(r * frag_dur, (r + 1) * frag_dur)
        return clip, r, d


def clip_resize(clip, width, length, method='crop'):
    """
    重写改变视频长宽高
    :param clip:
    :param width:
    :param length:
    :param method:
    :return:
    """
    o_width = clip.size[0]
    o_length = clip.size[1]
    if width is None and length is None:
        # 传参宽高都是None，返回原视频
        return clip
    # 处理宽度
    if width is not None:
        # 宽度不为None
        if o_width < width:
            # 如果设置的宽度比原视频的宽度要宽
            return None
        x1 = math.floor(o_width / 2 - width / 2)
        x2 = x1 + width
    else:
        x1 = 0
        x2 = o_width
    # 处理高度
    if length is not None:
        if o_length < length:
            # 如果设置的高度比原视频要低
            return None
        y1 = math.floor(o_length / 2 - length / 2)
        y2 = y1 + length
    else:
        y1 = 0
        y2 = o_length
    clip = clip.crop(x1, y1, x2, y2)
    return clip


def clip_add_margin(clip, w_l_ratio):
    """
    给视频补足，保证宽高比
    :param clip:
    :param w_l_ratio:
    :return:
    """
    o_width = clip.size[0]
    o_length = clip.size[1]
    if (o_width / o_length) / w_l_ratio > 1.01:
        # 比目标比例要宽，要增加上下的margin,原视频居中
        top = math.floor((o_width / w_l_ratio - o_length) / 2)
        bottom = math.floor((o_width / w_l_ratio - o_length) / 2)
        clip = margin(clip, top=top, bottom=bottom, color=(0, 0, 0))
        return clip
    elif (o_width / o_length) / w_l_ratio < 0.99:
        # 比目标比例要窄，要增加左右的margin，这种情况比较少
        left = math.floor((o_length * w_l_ratio - o_width) / 2)
        right = math.floor((o_length * w_l_ratio - o_width) / 2)
        clip = margin(clip, left=left, right=right, color=(0, 0, 0))
        return clip
    else:
        # 和目标比例差不多
        return clip


# @progress_bar_decorator(total_iterations=100)
def combineVideo(tim_len, video_type, frag_dur=30, speed=1, bitrate='3000k', codec='libx264', fps=30, write=True, ):
    """
    :param tim_len: 时间要求长度
    :param type: 视频类型，哪种类型的内容
    1080:1920 竖屏
    1080:720 横屏
    :return: 文件名
    固定的时长的素材
    """
    logger.assemble_logger.info('开始合并视频...')
    video_config = config.video_setting.get(video_type)
    context_path = video_config.get('path')
    frag_dur = video_config.get('frag_dur')
    if frag_dur is None:
        raise Exception('frag duration is None')
    filelog = ''
    dir = config.target_directory + '/' + '素材/' + context_path + '/'
    ft = FileTree(dir)
    file_list = ft.get_file_list()
    random.seed(time.time())
    current_dict = {}  # 已经添加的序号
    total_materials_length = 0  # 需要控制总时长，否则内存会爆，一般为目标时长的5倍，如果总素材的时长超过需求的5倍，则不再追加新素材，防止内存溢出
    first = random.randint(0, len(file_list) - 1)
    path = dir + file_list[first]
    clip_orginal = VideoFileClip(path)
    if fps is not None:
        fps = clip_orginal.fps
    total_materials_length += clip_orginal.duration
    clip, ini, total = sub_clip(clip_orginal, frag_dur * speed)
    clip = clip.speedx(speed)
    current_dict[first] = {'total': total, 'occupied_list': [ini], 'original_object': clip_orginal}
    # clip = resize(clip,width,length)
    if clip is None:
        raise Exception('素材尺寸不对')

    filelog += 'part: 1: from file : ' + file_list[first] + ' with slice ' + str(
        current_dict.get(first).get('occupied_list')[0]) + '\n'
    logger.assemble_logger.info('part: 1: from file : ' + file_list[first] + ' with slice ' + str(
        current_dict.get(first).get('occupied_list')[0]))
    idx = 2  # 循环的index
    while clip.duration < tim_len:
        if tim_len - clip.duration < frag_dur:
            tmp_frag_dur = tim_len - clip.duration
        else:
            tmp_frag_dur = frag_dur
        duplicate_flag = 0  # 是否重复使用同一个视频的内容
        if total_materials_length < tim_len * 5 or len(current_dict) >= math.ceil(len(file_list) * 0.8):
            # 加载时长最多不超过输出时长的5倍(防止内存占用过多) 或者是 当前列表里已经占用的视频超过80%的总资源
            next_i = random.randint(0, len(file_list) - 1)
            while next_i in current_dict:
                next_i = random.randint(0, len(file_list) - 1)
            next_clip_original = VideoFileClip(dir + file_list[next_i])
        else:
            duplicate_flag = 1
            next_i = random.choice(list(current_dict.keys()))
            while current_dict.get(next_i).get('total') < len(current_dict.get(next_i).get('occupied_list')) + 2:
                next_i = random.choice(list(current_dict.keys()))
            next_clip_original = current_dict.get(next_i).get('original_object')
        total_materials_length += next_clip_original.duration
        next_clip, i_ini, total = sub_clip(next_clip_original, tmp_frag_dur * speed)
        while i_ini in current_dict.get(next_i).get('occupied_list') if current_dict.get(next_i) is not None else False:
            next_clip, i_ini, total = sub_clip(next_clip_original, tmp_frag_dur * speed)
        next_clip = next_clip.speedx(speed)
        next_clip = next_clip.set_fps(fps)
        if duplicate_flag == 0:
            current_dict[next_i] = {'total': total, 'occupied_list': [i_ini], 'original_object': next_clip_original}
        else:
            current_dict.get(next_i).get('occupied_list').append(i_ini)
        filelog += 'part: ' + str(idx) + ': from file : ' + file_list[next_i] + ' with slice ' + str(
            current_dict.get(next_i).get('occupied_list')[-1]) + '\n'
        logger.assemble_logger.info('part: ' + str(idx) + ': from file : ' + file_list[next_i] + ' with slice ' + str(
            current_dict.get(next_i).get('occupied_list')[-1]))
        # print(f'current clip fps is {str(next_clip.fps)}, and main clip fps is {str(clip.fps)}')
        # next_clip = resize(next_clip, width=width, length=length)
        if next_clip is None:
            print('file : ' + file_list[next_i] + '素材尺寸不对')
            continue
        clip = concatenate_videoclips([clip, next_clip])
        idx += 1
    clip = clip.set_audio(None)
    # 改变尺寸
    clip = clip_resize(clip, width=video_config.get('width'), length=video_config.get('length'))
    # 补足成9:16的尺寸
    clip = clip_add_margin(clip=clip, w_l_ratio=9 / 16)
    # 改变分辨率
    new_resolutions = video_config.get('new_resolution')
    if new_resolutions is not None:
        # 这里更改了包里的resize文件的方法，resized_pil = pilim.resize(newsize[::-1], Image.LANCZOS)
        clip = clip.resize(new_resolutions)
    if write:
        output_folder = config.result_directory + '/' + video_type
        c_time = str(time.time()).split('.')[0]
        output_path = os.path.join(output_folder, c_time + '.mp4')
        # 确保输出文件夹路径存在，如果不存在则创建
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        with open(os.path.join(output_folder, c_time + '.txt'), 'w') as file:
            file.write(filelog)
        logger.assemble_logger.info('开始合并文件，输出中，请等待...')
        clip.write_videofile(output_path, codec='h264_videotoolbox', bitrate=bitrate, threads=24, fps=fps,
                             preset='medium', )
        logger.assemble_logger.info('文件合并已结束')
        return output_path
    else:
        return clip, filelog


if __name__ == '__main__':
    # for i in range(10):
    # combineVideo(tim_len=1200,type='解压素材',frag_dur=20,speed=1.5)
    # combineVideo(tim_len=1200, type='甜点饮品制作视频', frag_dur=20, speed=1)
    combineVideo(tim_len=120, video_type='蛋仔素材', frag_dur=30, speed=1)
    # combineVideo(sys.argv[0],sys.argv[1], sys.argv[2])
