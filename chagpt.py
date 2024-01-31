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
OPENAI_API_KEY='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'
client = OpenAI(api_key=OPENAI_API_KEY)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)