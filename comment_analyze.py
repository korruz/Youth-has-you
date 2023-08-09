from __future__ import print_function

import json
import re  # 正则匹配
import time

import jieba  # 中文分词
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import paddlehub as hub
import requests
from PIL import Image
from wordcloud import WordCloud  # 绘制词云模块


# 请求爱奇艺评论接口，返回response信息
def getMovieinfo(url):
    """
    请求爱奇艺评论接口，返回response信息
    参数  url: 评论的url
    :return: response信息
    """
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "http://m.iqiyi.com/v_19rqriflzg.html",
        "Origin": "http://m.iqiyi.com",
        "Host": "sns-comment.iqiyi.com",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
        "Accept-Encoding": "gzip, deflate",
    }
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


# 解析json数据，获取评论
def saveMovieInfoToFile(lastId, arr):
    """
    解析json数据，获取评论
    参数  lastId:最后一条评论ID  arr:存放文本的list
    :return: 新的lastId
    """
    url = "https://sns-comment.iqiyi.com/v3/comment/get_comments.action?agent_type=118&\
    agent_version=9.11.5&business_type=17&content_id=15068699100&page=&page_size=10&types=time&last_id="
    url += str(lastId)
    responseTxt = getMovieinfo(url)
    responseJson = json.loads(responseTxt)
    comments = responseJson["data"]["comments"]
    for val in comments:
        # print(val.keys())
        if "content" in val.keys():
            # print(val['content'])
            arr.append(val["content"])
        lastId = str(val["id"])
    return lastId


# 去除文本中特殊字符
def clear_special_char(content):
    """
    正则处理特殊字符
    参数 content:原文本
    return: 清除后的文本
    """
    s = re.sub(r"</?(.+?)>|&nbsp;|\t|\r", "", content)
    s = re.sub(r"\n", " ", s)
    s = re.sub("[^\u4e00-\u9fa5^a-z^A-Z^0-9]", "", s)

    return s


def fenci(text):
    """
    利用jieba进行分词
    参数 text:需要分词的句子或文本
    return：分词结果
    """
    jieba.load_userdict("add_words.txt")  # 添加自定义字典
    seg = jieba.lcut(text, cut_all=False)
    return seg


def stopwordslist(file_path):
    """
    创建停用词表
    参数 file_path:停用词文本路径
    return：停用词list
    """
    stopwords = [line.strip() for line in open(file_path, encoding="UTF-8").readlines()]
    return stopwords


def movestopwords(sentence, stopwords, counts):
    """
    去除停用词,统计词频
    参数 file_path:停用词文本路径 stopwords:停用词list counts: 词频统计结果
    return：None
    """
    out = []
    for word in sentence:
        if word not in stopwords:
            if len(word) != 1:
                counts[word] = counts.get(word, 0) + 1
    return None


def drawcounts(counts, num):
    """
    绘制词频统计表
    参数 counts: 词频统计结果 num:绘制topN
    return：none
    """
    x_aixs = []
    y_aixs = []
    c_order = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    # print(c_order)
    for c in c_order[:num]:
        x_aixs.append(c[0])
        y_aixs.append(c[1])

    # 设置显示中文
    matplotlib.rcParams["font.sans-serif"] = ["SimHei"]  # 指定默认字体
    matplotlib.rcParams["axes.unicode_minus"] = False  # 解决保存图像是负号'-'显示为方块的问题
    plt.bar(x_aixs, y_aixs)
    plt.title("词频统计结果")
    plt.show()


def drawcloud(word_f):
    """
    根据词频绘制词云图
    参数 word_f:统计出的词频结果
    return：none
    """
    # 加载背景图片
    cloud_mask = np.array(Image.open("cluod.png"))
    # 忽略显示的词
    st = set(["东西", "这是"])
    # 生成wordcloud对象
    wc = WordCloud(
        background_color="white",
        mask=cloud_mask,
        max_words=150,
        font_path="simhei.ttf",
        min_font_size=10,
        max_font_size=100,
        width=400,
        relative_scaling=0.3,
        stopwords=st,
    )
    wc.fit_words(word_f)
    wc.to_file("pic.png")


def text_detection(text, file_path):
    """
    使用hub对评论进行内容分析
    return：none
    """
    porn_detection_lstm = hub.Module(name="porn_detection_lstm")
    f = open("aqy.txt", "r", encoding="utf-8")
    for line in f:
        if len(line.strip()) == 1:  # 判断评论长度是否为1
            continue
        else:
            test_text.append(line)
    f.close()
    input_dict = {"text": test_text}
    results = porn_detection_lstm.detection(data=input_dict, use_gpu=True, batch_size=1)
    # print(results)
    for index, item in enumerate(results):
        if float(item["porn_probs"]) > 0.95:
            print(item["text"], ":", item["porn_probs"])


# 评论是多分页的，得多次请求爱奇艺的评论接口才能获取多页评论,有些评论含有表情、特殊字符之类的
# num 是页数，一页10条评论，假如爬取1000条评论，设置num=100
if __name__ == "__main__":
    num = 20
    lastId = "0"  # lastId 是接口分页id
    arr = []  # arr是爬取的所有评论存放的数组
    with open("aqy.txt", "a", encoding="utf-8") as f:  # 写文件是追加写的
        for i in range(num):
            lastId = saveMovieInfoToFile(lastId, arr)
            # print(i)
            time.sleep(0.5)  # 频繁访问爱奇艺接口，偶尔出现接口连接报错情况，睡眠0.5秒，增加每次访问间隔时间
        for item in arr:
            Item = clear_special_char(item)
            # print(Item)
            if Item.strip() != "":
                try:
                    f.write(Item + "\n")
                except Exception as e:
                    print("含有特殊字符")
    print("共爬取评论：", len(arr))
    f = open("aqy.txt", "r", encoding="utf-8")
    counts = {}
    for line in f:
        words = fenci(line)
        stopwords = stopwordslist("cn_stopwords.txt")
        movestopwords(words, stopwords, counts)

    drawcounts(counts, 10)  # 绘制top10 高频词
    drawcloud(counts)  # 绘制词云
    f.close()

    """
    使用hub对评论进行内容分析
    """
    file_path = "aqy.txt"
    test_text = []
    text_detection(test_text, file_path)
    Image.open("pic.png").show()  # 显示生成的词云图像
