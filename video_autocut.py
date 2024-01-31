# Import everything needed to edit video clips
import multiprocessing
from datetime import datetime
from tqdm import tqdm
from multiprocessing import Pool,Process
from concurrent.futures import ProcessPoolExecutor
from moviepy.editor import *
import math
import os
import random
import time
from moviepy.video.fx.all import *

# 指定要构建目录树的目录
target_directory = "/Volumes/公共空间/解压视频"

video_directory = "/Volumes/公共空间/配音文件/短片"

result_directory = "/Volumes/公共空间/产出视频"


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


def sub_clip(clip, frag_dur,):
    d = clip.duration / frag_dur
    if d < 1:
        return clip,0
    else:
        d = math.floor(d)
        if d <=2:
            r = 0 # 取中间
        else:
            random.seed(time.time())
            r = random.randint(0, d - 1)
        # 掐头去尾
        clip = clip.subclip(r * frag_dur, (r + 1) * frag_dur)
        return clip,r



def resize(clip,width,length,method='crop'):
    # o_width = clip.size[0]
    # o_length = clip.size[1]
    # if float(width/length) > float(o_width/o_length):
    #     """ 需要变宽 """
    #     x1 = 0
    #     x2 = o_width
    #     y1 = o_length/2 - o_width * float(length / width) / 2
    #     y2 = o_length/2 + o_width * float(width / length) / 2
    #     clip = clip.crop(x1, y1, x2, y2)
    # elif float(width/length) < float(o_width/o_length):
    #     """ 需要变窄 """
    #     y1 = 0
    #     y2 = o_length
    #     x1 = o_width/2 - o_length * float(width / length) / 2
    #     x2 = o_width/2 + o_length * float(width / length) / 2
    #     clip = clip.crop(x1, y1, x2, y2)
    clip = clip.fx(vfx.resize, width=width, height=length)
    return clip

# @progress_bar_decorator(total_iterations=100)
def combineVideo(tim_len,type,width=1080,length=1920, frag_dur=None, speed=1, bitrate='5000k', codec='libx264', fps=30):
    """
    :param tim_len: 时间要求长度
    :param type: 视频类型，哪种类型的内容
    :return: 文件名
    """
    print('start combineVideo')
    filelog = ''
    dir = target_directory + '/' + '素材/' + type + '/'
    ft = FileTree(dir)
    file_list = ft.get_file_list()
    random.seed(time.time())
    current_list = []  # 已经添加的序号
    first = random.randint(0, len(file_list)-1)
    path = dir + file_list[first]
    clip = VideoFileClip(path)
    if fps is not None:
        fps = clip.fps
    if frag_dur is not None:
        clip, ini = sub_clip(clip, frag_dur*speed)
        clip = clip.speedx(speed)
        current_list.append((first, ini))
    else:
        current_list.append((first, 0))
    clip = resize(clip,width=width,length=length)
    filelog += 'part: 1: from file : '+file_list[first] + ' with slice ' + str(current_list[-1][1]) + '\n'
    while clip.duration < tim_len:
        next_i = random.randint(0, len(file_list) - 1)
        while next_i in current_list:
            next_i = random.randint(0, len(file_list)-1)
        next_clip = VideoFileClip(dir + file_list[next_i])
        if frag_dur is not None:
            next_clip, i_ini = sub_clip(next_clip, frag_dur*speed)
            next_clip = next_clip.speedx(speed)
            current_list.append((next_i, i_ini))
        else:
            current_list.append((next_i,0))
        filelog += 'part: '+ str(len(current_list)) +': from file : ' + file_list[first] + ' with slice ' + str(current_list[-1][1]) + '\n'
        # clip = clip.fx(vfx.resize,width=width,height=length)
        next_clip = resize(next_clip, width=width, length=length)
        clip = concatenate_videoclips([clip, next_clip])
        # if pbar is not None:
        #     pbar.update(float(frag_dur/tim_len)*100)
    clip = clip.set_audio(None)
    # 拉伸
    # clip = clip.fx(vfx.resize, width=width, height=length)
    # 裁剪切割
    # clip = resize(clip, width, length)
    output_folder = result_directory + '/' + type + '/' + datetime.now().date().strftime("%Y%m%d")
    c_time = str(time.time()).split('.')[0]
    output_path = os.path.join(output_folder, c_time + '.mp4')
    # 确保输出文件夹路径存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(os.path.join(output_folder,c_time + '.txt'), 'w') as file:
        file.write(filelog)
    clip.write_videofile(output_path, codec='h264_videotoolbox', bitrate=bitrate,threads=24, fps=fps, preset='medium', )

    print('end combineVideo')




if __name__ == '__main__':

    for i in range(10):
        # combineVideo(tim_len=1200,type='解压素材',frag_dur=20,speed=1.5)
        combineVideo(tim_len=1200, type='甜点饮品制作视频', frag_dur=20, speed=1)
        combineVideo(tim_len=1200, type='甜点饮品制作视频', frag_dur=20, speed=1)
    #combineVideo(sys.argv[0],sys.argv[1], sys.argv[2])

