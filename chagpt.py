'''
coding:utf-8
@FileName:chagpt
@Time:2024/1/26 10:55 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''

from openai import OpenAI



# Once you add your API key below, make sure to not share it with anyone! The API key should remain private.
from factory.assembler import push_to_mq_test

OPENAI_API_KEY='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'
# client = OpenAI(api_key=OPENAI_API_KEY)
#
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )
#
# print(completion.choices[0].message)


if __name__ == '__main__':
    push_to_mq_test({'book_id': '7352783803380679192', 'alias': '若若不差钱', 'book_name': '太子党全都装穷耍我', 'account': 34663015465, 'filepath': '/Volumes/home/小说推文/产出视频/成片2024-06-19/34663015465/7352783803380679192_太子党全都装穷耍我', 'title': '🍅小说sou:《若若不差钱》', 'type': 'douyin_short', 'description': '今天是弟弟姜枫的生日，我找老板预支100块工资提前半天下了班，打算给他个惊喜。说实话还有点肉痛，要知道这可是家里一星期的伙食费。为了省2块钱的公交车费，我决定步行回家。走到楼下后我脚步一顿，抬手揉了揉眼睛，怔愣地看着一辆豪车停在我们这个破烂小区', 'img_path': '/Volumes/home/小说推文/产出视频/成片2024-06-19/34663015465/7352783803380679192_太子党全都装穷耍我/cover.png', 'platform': 'fanqie', 'publish_time': '2024-6-19 11:39', 'content_type': 'short_novel'})
