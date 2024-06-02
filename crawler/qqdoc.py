'''
coding:utf-8
@FileName:qqdoc
@Time:2024/6/2 12:13 AM
@Author: Xiang Xiao
@Email: btxiaox@gmail.com
@Description:
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd


# 文档的URL


def get_docs(url,type = 'table'):
    """
    获取文档信息
    :param type: str
    :param url: str
    :return: DataFrame
    """
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
   }

    # 发送GET请求
    response = requests.get(url, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取表格数据
        if type == 'table':
            table = soup.find('table')
            # 将表格数据转换为DataFrame
            df = pd.read_html(str(table))[0]
            # 删除索引
            df = df.drop(columns=['Unnamed: 0'])
            # 删除空行
            df = df.dropna(how='all',axis=1).dropna(how='all',axis=0)
            # 将 DataFrame 转换为 list of dicts，第一行作为 key
            results = df.iloc[1:].to_dict(orient='records')
            keys = df.iloc[0].to_dict()

            # 替换每个字典中的 key
            results = [{keys[k]: v for k, v in row.items()} for row in results]
            for re in results:
                # 调整publish_time的格式，目前的格式是'YYYY/MM/DD HH:MM' 变成'YYYY-MM-DD HH:MM'
                re['publish_time'] = re['publish_time'].replace('/', '-')
                # # 调整编码
                # re['bgm_name'] = re['bgm_name'].decode('utf-8')
                # re['account'] = re['account'].decode('utf-8')

            return results
        else:
            return []
    else:
        print("Failed to retrieve data")



if __name__ == '__main__':
    url = 'https://docs.qq.com/sheet/DV0lpTWRaYXZnRXJC?tab=BB08J2'
    print(get_docs(url = url))