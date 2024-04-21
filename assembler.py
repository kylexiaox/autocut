'''
coding:utf-8
@FileName:assembler
@Time:2024/1/20 7:11 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''
import config
from text import *
from dub import *
from video_autocut import *
from moviepy.audio.fx.volumex import volumex
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
import pysrt
import re
from PIL import Image
import speech_recognition as sr


def assembler(bookid, bgm_name, alias, content_type=0, voice_type='female', bgm_volume=0.15, video_type='西餐美食小吃视频',
              bitrate='3000k', cover_img='girl1', is_landscape=False):
    # 获取内容音频
    audio_clip, srt_path, book_name = get_text_voice(bookid, content_type=content_type, voice_type=voice_type)
    # 音量标准化
    audio_clip = audio_clip.audio_normalize()
    video_len = audio_clip.duration
    print(f'处理BGM,BGM使用的是{bgm_name}')
    bgm_clip = AudioFileClip(config.bgm_directory + bgm_name + '/head.MP3').audio_normalize()
    bgm_tail_clip = AudioFileClip(config.bgm_directory + bgm_name + '/tail.MP3').audio_normalize()
    if video_len > bgm_clip.duration:
        tmp_bgm_clip = afx.audio_loop(bgm_tail_clip, duration=(video_len - bgm_clip.duration))
        bgm_clip = concatenate_audioclips([bgm_clip, tmp_bgm_clip])
    else:
        bgm_clip = bgm_clip.subclip(t_start=0, t_end=video_len)
    bgm_clip = bgm_clip.fx(volumex, bgm_volume)

    print(f'处理音频，合并BGM和内容音频')
    overlay_audio_clip = CompositeAudioClip([audio_clip, bgm_clip])

    print(f'合并解压视频素材')
    video_clip, filelog = combineVideo(tim_len=overlay_audio_clip.duration, type=video_type, frag_dur=30, speed=1,
                                       write=False)
    print(f'音视频合并')
    video_clip = video_clip.set_audio(overlay_audio_clip)
    # 创建字幕文本剪辑
    print('处理字幕')
    video_clip = add_srt_to_video(srt_path, video_clip, font=config.font.get('字魂大黑'))
    print('处理标题别名')
    label_text = config.label_str.get('fanqie') + '\n《' + alias + '》'
    final_clip = add_label_to_video(text=label_text, pic_file=config.icon_file.get('fanqie'), video_clip=video_clip,
                                    font=config.font.get('字魂劲道黑'))
    output_folder = config.result_directory + '/' + str(bookid) + '_' + book_name
    c_time = str(time.time()).split('.')[0]
    output_path = os.path.join(output_folder, str(bookid) + '_' + bgm_name + '.mp4')
    # 确保输出文件夹路径存在，如果不存在则创建
    print('输出目录为 : ' + output_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(os.path.join(output_folder, c_time + '_' + str(bookid) + '_log.txt'), 'w') as file:
        file.write(filelog)
    fps = final_clip.fps
    final_clip.write_videofile(output_path, codec='h264_videotoolbox', bitrate=bitrate, threads=24, fps=fps,
                               preset='medium', )
    print('视频文件写入完成')
    print("处理封面")
    get_cover_img(text="《{alias}》", img=cover_img, output_folder=output_folder )
    return output_path


def get_text_voice(bookid, content_type=0, voice_type='female'):
    """
    通过bookid拿音频+字幕
    :param bookid:
    :param content_type:
    :param voice_type:
    :return:
    """
    if content_type == 0:
        # 短篇
        print(f"获取音频文件：{bookid}")
        bookinfo = get_book_info(bookid)
        text = get_content_from_fanqie_dp(bookid)
        texts = split_content(text, gap=6000, end_with='。')
        paths = []
        for index, text in enumerate(texts):
            paths.append(dubbing_for_long(long_text=text, result_filename=str(bookinfo[0]) + '_' + str(index),
                                          voice_type=voice_type,
                                          output_dir=config.result_directory + '/' + str(bookid) + '_' + bookinfo[0],
                                          flag=True))
        info_str = 'book_id : ' + str(bookinfo[2]) + '\n'
        info_str += 'book_name : ' + bookinfo[0] + '\n'
        info_str += 'abstract : ' + bookinfo[1]
        final_output_folder = config.result_directory + '/' + str(bookid) + '_' + bookinfo[0]
        if not os.path.exists(final_output_folder):
            os.makedirs(final_output_folder)
        with open(config.audio_directory_short + bookinfo[0] + '_info.txt', 'wb') as file:
            file.write(info_str.encode('UTF-8'))
        with open(os.path.join(final_output_folder, bookinfo[0] + '_info.txt'), 'wb') as file:
            file.write(info_str.encode('UTF-8'))
        with open(os.path.join(final_output_folder, bookinfo[0] + '_text.txt'), 'wb') as file:
            file.write(text.encode('UTF-8'))
        with open(config.audio_directory_short + bookinfo[0] + '_text.txt', 'wb') as file:
            file.write(text.encode('UTF-8'))
        audio_clip = None
        for path in paths:
            if audio_clip is None:
                audio_clip = AudioFileClip(path[0])
            else:
                audio_clip = concatenate_audioclips([audio_clip, AudioFileClip(path[0])])
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


def add_srt_to_video(srt_file, video_clip, font="/Users/xiangxiao/Documents/Fonts/yezigongchanghuajuanti.ttf"):
    print(f'添加字幕文件到视频中，字幕文件{srt_file}')
    def generate_text(txt):
        txt = remove_non_alphanumeric(txt)
        return TextClip(txt, font=font, fontsize=40, color='white', stroke_color='black', stroke_width=1,
                        method='caption', size=(450, None))

    subtitles = SubtitlesClip(srt_file, generate_text)
    result = CompositeVideoClip([video_clip, subtitles.set_position(('center', 650), relative=False)])
    # 输出结果视
    # result.write_videofile("output.mp4",fps=video.fps)
    return result


def add_label_to_video(text, pic_file, video_clip, font='Arial Unicode MS', size=(300, None),
                       txt_position=('center', 300),pic_position=('center', 200)):
    text_clip = TextClip(text, font=font, fontsize=30, color='black', stroke_color='white', stroke_width=2, size=size)
    text_clip = text_clip.set_position(txt_position)
    text_clip = text_clip.set_duration(video_clip.duration)
    pic_clip = ImageClip(pic_file)
    pic_clip = pic_clip.set_duration(video_clip.duration)
    pic_clip = pic_clip.set_position(pic_position)
    pic_clip = pic_clip.resize(width=60, height=60)
    video_with_pic = CompositeVideoClip([video_clip, pic_clip])
    video_with_text = CompositeVideoClip([video_with_pic, text_clip])
    # video_with_text.write_videofile("output.mp4",fps=video_clip.fps)
    return video_with_text


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


def remove_non_alphanumeric(text):
    # 使用正则表达式匹配任何非字母数字字符，并将其替换为空字符串
    return re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)


def get_cover_img(text,img,output_folder="", font='字魂劲道黑',):
    # 打开图像文件
    img = Image.open(config.cover_img.get(img))
    # 计算裁剪的区域
    left = math.floor(img.size[0] / 2 - math.floor(img.size[0] * 0.75 / 2))
    right = math.floor(img.size[0] / 2 + math.floor(img.size[0] * 0.75 / 2))
    top = 0
    bottom = img.size[1]
    # 裁剪图像
    cropped_image = img.crop((left, top, right, bottom))
    cropped_image.save('tmp_cover.png')
    # 创建 ImageClip 对象
    img_clip = ImageClip('tmp_cover.png')
    # 创建文本剪辑
    text_clip = TextClip(txt=text, font=config.font.get(font), fontsize=60, color='white', stroke_color='black', stroke_width=3)
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
    final_image_pil.save(output_folder+'/'+"cover.png")



if __name__ == '__main__':
    # assembler(bookid=7329015211099161150,bgm_name='面会菜')
    # assembler(bookid=7343205340197948478,bgm_name='悬溺') ## 成为金丝雀后，我把金主送进监狱
    # assembler(bookid=7308997941211958287, bgm_name='赤伶')
    # assembler(bookid=7299700258157068839, bgm_name='凄美地')
    # assembler(bookid=7331557786192462398, bgm_name='冬眠')
    #  assembler(bookid=7316840792012622902, bgm_name='暖一杯茶',voice_type='male')
    # assembler(bookid=7282959964250112575, bgm_name='凄美地', voice_type='male')
    # assembler(bookid=7268209171302976572, bgm_name='悬溺', voice_type='female')
    # assembler(bookid=7296749431120989199, bgm_name='暖一杯茶', voice_type='male')
    # assembler(bookid=7198112366377045007, bgm_name='富士山下', voice_type='female')
    # assembler(bookid=7246613580164893700, bgm_name='赤伶', voice_type='male')
    # assembler(bookid=7281033423756460585, bgm_name='桃花诺', voice_type='female')
    # assembler(bookid=7281033423756460585, bgm_name='悬溺', voice_type='female',video_type='甜点饮品制作视频')
    # assembler(bookid=7133168611677766151, bgm_name='凄美地', voice_type='female', video_type='甜点饮品制作视频')
    # assembler(bookid=7286117680602415650, bgm_name='暖一杯茶', voice_type='male', video_type='甜点饮品制作视频')
    # assembler(bookid=7321928877381520446, bgm_name='悬溺', voice_type='female', video_type='甜点饮品制作视频')
    # assembler(bookid=7211026420175211576, bgm_name='悬溺', voice_type='female', video_type='/蛋仔素材/2023年 6月-12月更新/竞速图',is_landscape=True)
    # assembler(bookid=7286117680602415650, bgm_name='冬眠', voice_type='male', video_type='/蛋仔素材/2023年 6月-12月更新/竞速图',
    #           is_landscape=True)
    # assembler(bookid=7314551982457359412, bgm_name='悬溺', voice_type='male', video_type='/蛋仔素材/2023年 6月-12月更新/竞速图',
    #           is_landscape=True)
    # assembler(bookid=7321928877381520446, bgm_name='富士山下', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7211026420175211576, bgm_name='梦回仙游', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7286117680602415650, bgm_name='冬眠', voice_type='male', video_type='迷你厨房')
    # assembler(bookid=7250397143100457487, bgm_name='暖一杯茶', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7272308977575136275, bgm_name='用情', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7264865084881505314, bgm_name='面会菜', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7301877628695219240, bgm_name='桃花诺', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7314551982457359412, bgm_name='桃花诺', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7308715470624918540, bgm_name='梦回仙游', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7331651841098271806, bgm_name='桃花诺', voice_type='female', video_type='迷你厨房')
    # srts = ['/Volumes/公共空间/小说推文/产出视频/成片/7314551982457359412_我死后，妻子后悔了/我死后，妻子后悔了_0.srt','/Volumes/公共空间/小说推文/产出视频/成片/7314551982457359412_我死后，妻子后悔了/我死后，妻子后悔了_1.srt']
    # merge_srt(srts)
    # assembler(bookid=7123506139219627047, bgm_name='悬溺', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7271510621655403561, bgm_name='暖一杯茶', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7290092833015333439, bgm_name='富士山下', voice_type='female', video_type='迷你厨房')
    # assembler(bookid=7322348136427424830, bgm_name='冬眠', voice_type='female', video_type='迷你厨房')
    # add_srt_to_video('/Volumes/公共空间/小说推文/产出视频/成片/2024-04-14/7290092833015333439_金主破产后我包养了他/金主破产后我包养了他.srt',
    #                  '/Volumes/公共空间/小说推文/产出视频/成片/2024-04-14/7290092833015333439_金主破产后我包养了他/7290092833015333439_富士山下.mp4',
    #                  font='/Users/xiangxiao/Documents/Fonts/字魂劲道黑.ttf')
    # add_label_to_video(text = '🍅小说sou:《美女爱上我》',pic_file='fanqie.png',font='/Users/xiangxiao/Documents/Fonts/字魂劲道黑.ttf')

    # output_path = assembler(bookid=7173533120174492704, bgm_name='冬眠', voice_type='female', video_type='迷你厨房',
    #                         alias='冷月清秋')
    edit_cover_img()
