import asyncio
import datetime
import json
import os
import re
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

# 获取当天的日期,并进行格式化,用于后面文件命名，格式:20200420
today = datetime.date.today().strftime('%Y%m%d')


async def fetch(url):
    """
    获取网页内容
    :param url: 网址
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"获取网页内容失败：{url}")
                return None


async def download_image(url):
    """
    获取图片内容
    :param url: 网址
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"获取图片内容失败：{url}")
                return None


async def crawl_wiki_data():
    url = "https://baike.baidu.com/item/青春有你第二季"
    response = await fetch(url)
    print("发起请求...")
    if response is None:
        return
    else:
        soup = BeautifulSoup(response, 'lxml')
        div = soup.find_all('div', {"data-uuid": 'gny2nzwxeh'})
        if len(div):
            tables = div[0].find_all_next('tbody')
            if len(tables):
                table = tables[0]
                await parse_wiki_data(table)
            else:
                print("tables 内容不存在")
        else:
            print("data-uuid 内容不存在")


async def parse_wiki_data(table_html):
    """
    从百度百科返回的html中解析得到选手信息，以当前日期作为文件名，存JSON文件,保存到work目录下
    """
    print("解析 table 数据...")
    bs = BeautifulSoup(str(table_html), 'lxml')
    all_trs = bs.find_all('tr')

    error_list = ['\'', '\"']

    stars = []

    for tr in all_trs[1:]:
        all_tds = tr.find_all('td')

        star = {}

        if all_tds[0].find('a') is None:
            # 姓名
            star["name"] = all_tds[0].find('span').text
            # 个人百度百科链接
            star["link"] = ''
        else:
            star["name"] = all_tds[0].find('a').text
            star["link"] = 'https://baike.baidu.com' + all_tds[0].find('a').get('href')
        # 籍贯
        star["zone"] = all_tds[1].find('span').text
        # 星座
        star["constellation"] = all_tds[2].find('span').text

        # 花语,去除掉花语中的单引号或双引号
        flower_word = all_tds[3].find('span').text
        for c in flower_word:
            if c in error_list:
                flower_word = flower_word.replace(c, '')
        star["flower_word"] = flower_word

        # 公司
        if not all_tds[4].find('a') is None:
            star["company"] = all_tds[4].find('a').text
        else:
            star["company"] = all_tds[4].find('span').text

        stars.append(star)

    json_data = json.loads(str(stars).replace("\'", "\""))
    print("写入数据到 work 目录中...")
    with open('work/' + today + '.json', 'w', encoding='UTF-8') as f:
        json.dump(json_data, f, ensure_ascii=False)


async def crawl_pic_urls():
    """
    爬取每个选手的百度百科图片，并保存
    """
    with open('work/' + today + '.json', 'r', encoding='UTF-8') as file:
        json_array = json.loads(file.read())

    for index, star in enumerate(json_array):
        name = star['name']
        link = star['link']

        base_url = "https://baike.baidu.com/pic/{}/{}/1/{}?fromModule=lemma_top-image&ct=single#aid=1&pic={}"

        # ！！！请在以下完成对每个选手图片的爬取，将所有图片url存储在一个列表pic_urls中！！！
        pic_urls = []
        if len(link):
            response = await fetch(link)
            print(f"发起对 {index}-{name} 的请求...")
            soup = BeautifulSoup(response, 'lxml')
            name = soup.select('[data-lemmatitle]')[0].get("data-lemmatitle")
            name_x = quote(name, encoding='utf-8')
            uid = soup.find('div', {'data-lemmatitle': name}).get("data-lemmaid")
            matches = re.findall(r'"origSrc":"([^"]+)"', str(soup))
            album_id = None
            if len(matches):
                album_id = matches[0]

            album_url = base_url.format(name_x, uid, album_id, album_id)
            album_response = await fetch(album_url)
            soup = BeautifulSoup(album_response, 'lxml')
            url_datas = soup.find('div', {'class', 'pic-list'})

            for url_data in url_datas.select('a img'):
                url = url_data.get('src')
                pic_urls.append(url)

        # ！！！根据图片链接列表pic_urls, 下载所有图片，保存在以name命名的文件夹中！！！
        await down_pic(name, pic_urls)


async def down_pic(name, pic_urls):
    """
    根据图片链接列表pic_urls, 下载所有图片，保存在以name命名的文件夹中,
    """
    path = 'work/' + 'pics/' + name + '/'

    if not os.path.exists(path):
        os.makedirs(path)

    for i, pic_url in enumerate(pic_urls):
        try:
            pic = await download_image(pic_url)
            string = str(i + 1) + '.jpg'
            with open(path + string, 'wb') as f:
                f.write(pic)
                print('成功下载第%s张图片: %s' % (str(i + 1), str(pic_url)))
        except Exception as e:
            print('下载第%s张图片时失败: %s' % (str(i + 1), str(pic_url)))
            print(e)
            continue


if __name__ == "__main__":
    # asyncio.run(crawl_pic_urls())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl_pic_urls())
