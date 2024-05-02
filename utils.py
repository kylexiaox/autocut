'''
coding:utf-8
@FileName:utils
@Time:2024/5/3 12:45 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''


def count_chinese_characters(input_string):
    count = 0
    for char in input_string:
        # 判断字符是否是汉字
        if '\u4e00' <= char <= '\u9fff':
            count += 1
    return count

def split_content(input_string,gap,end_with):
    """
    切割字符串
    :param input_string:
    :param count:
    :param end_with:
    :return:
    """
    print(len(input_string))
    start = 0
    results = []
    for index, char in enumerate(input_string):
        if (index-start) > (gap-50):
            if char == end_with:
                results.append(input_string[start:index+1])
                start = index+1
                continue
            if (index-start) == gap:
                results.append(input_string[start:index+1])
                start = index + 1
                continue
        if index == len(input_string)-1:
            results.append(input_string[start:index+1])
    return results


def remove_non_utf8(s):
    # 尝试将字符串编码为UTF-8，如果失败则捕获UnicodeEncodeError异常
    try:
        s.encode(encoding='utf-8')
        return s
    except UnicodeEncodeError:
        return ''

def trim(s):
    s.replace('*','')
    return s