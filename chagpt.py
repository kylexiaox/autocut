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
    push_to_mq_test({'book_id': 7348020574980951102, 'alias': '备胎日记', 'book_name': '不当舔狗后', 'account': 47040731565,
                   'filepath': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-12/7348020574980951102_不当舔狗后',
                   'title': '番茄小说sou：《备胎日记》',
                   'type': 'douyin_short',
                   'description': '在一起的第六年，我跟许钰提了分手。原因是我在她的车上看到了猫毛。而她从来不让我的猫上她的车，她说她有洁癖。听我这么说她无所谓的耸肩：[就因为这个？]因为这个，也不只因为是这个',
                   'img_path': '/Volumes/公共空间/小说推文/产出视频/成片/2024-05-12/7348020574980951102_不当舔狗后/cover.png',
                   'platform': 'fanqie',
                   'publish_time': '2024-06-01 11:00', 'content_type': 'short_novel'})
