'''
coding:utf-8
@FileName:assembler
@Time:2024/1/20 7:11 PM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''

from text import *
from dub import *
from video_autocut import *
from moviepy.audio.fx.volumex import volumex
import speech_recognition as sr


def assembler(bookid, bgm_name, content_type=0, voice_type='female',bgm_volume=0.2,video_type='西餐美食小吃视频',bitrate='3000k' ):
    print('start get audio_clip:######')
    audio_clip,book_name = get_text_voice(bookid, content_type=content_type, voice_type=voice_type)
    print('end get audio_clip:######')
    # audio_clip = AudioFileClip(config.audio_directory_short+'初心为何暗许_1.mp3')
    audio_clip = audio_clip.audio_normalize()

    video_len = audio_clip.duration
    print('start get bgm_clip:######')
    bgm_clip = AudioFileClip(config.bgm_directory + bgm_name + '/head.MP3').audio_normalize()
    bgm_tail_clip = AudioFileClip(config.bgm_directory + bgm_name + '/tail.MP3').audio_normalize()
    if video_len>bgm_clip.duration:
        tmp_bgm_clip = afx.audio_loop(bgm_tail_clip,duration=(video_len-bgm_clip.duration))
        bgm_clip = concatenate_audioclips([bgm_clip, tmp_bgm_clip])
    else:
        bgm_clip = bgm_clip.subclip(t_start=0,t_end=video_len)
    bgm_clip = bgm_clip.fx(volumex,bgm_volume)
    print('end get bgm_clip:######')
    print('start combine audio:######')
    overlay_audio_clip = CompositeAudioClip([audio_clip,bgm_clip])
    print('end combine audio:######')
    # overlay_audio_clip.write_audiofile(filename='test.mp3',fps=44100)
    print('start get video:######')
    video_clip,filelog = combineVideo(tim_len=overlay_audio_clip.duration, type=video_type, frag_dur=15, speed=1,write=False)
    print('end get video:######')
    print('assmebling :######')
    final_clip = video_clip.set_audio(overlay_audio_clip)
    output_folder = config.result_directory + '/' + '成片/'+str(bookid)+'_'+book_name
    c_time = str(time.time()).split('.')[0]
    output_path = os.path.join(output_folder, str(bookid) + '_' + bgm_name + '.mp4')
    # 确保输出文件夹路径存在，如果不存在则创建
    print('output path : '+ output_path+' and now is writing files')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(os.path.join(output_folder, c_time+'_'+ str(bookid) + '_log.txt'), 'w') as file:
        file.write(filelog)

    fps = final_clip.fps
    final_clip.write_videofile(output_path, codec='h264_videotoolbox', bitrate=bitrate, threads=24, fps=fps,
                         preset='medium', )
    print('end combineVideo')
    return output_path



def get_text_voice(bookid, content_type=0, voice_type='female'):
    if content_type == 0:
        # 短篇
        bookinfo = get_book_info(bookid)
        text = get_content_from_fanqie_dp(bookid)
        texts = split_content(text, gap=6000, end_with='。')
        paths = []
        for index, text in enumerate(texts):
            paths.append(dubbing_for_long(long_text=text, result_filename=str(bookinfo[0]) + '_' + str(index),
                                           voice_type=voice_type))

        info_str = 'book_id : ' + str(bookinfo[2]) + '\n'
        info_str += 'book_name : ' + bookinfo[0] + '\n'
        info_str += 'abstract : ' + bookinfo[1]
        final_output_folder = config.result_directory + '/' + '成片/'+str(bookid)+'_'+ bookinfo[0]
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
        return audio_clip,bookinfo[0]
    else:
        # 长篇
        pass


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
    assembler(bookid=7133168611677766151, bgm_name='凄美地', voice_type='female', video_type='甜点饮品制作视频')
    assembler(bookid=7286117680602415650, bgm_name='暖一杯茶', voice_type='male', video_type='甜点饮品制作视频')



