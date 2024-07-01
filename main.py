import time
import random
import os
import json
import csv
import re
import requests
from lxml import etree

with open('./AppData/USER_AGENTS.json', 'r', encoding='UTF-8') as file:
    USER_AGENTS = json.load(file)
with open('./AppData/CITY_CODE.json', 'r', encoding='UTF-8') as file:
    CITY_CODE = json.load(file)

def get_html(url: str, headers: dict) -> str:
    """网络请求, 获取页面 html 代码"""
    headers['User-Agent'] = random.choice(USER_AGENTS)
    try:
        response = requests.get(url=url, headers=headers, timeout=3)
        return response.text
    except Exception:
        time.sleep(random.random())
        return get_html(url, headers)

def categorise(details: list) -> dict:
    """将房屋细节 list 转化为 dict"""
    features = {
        'configuration': ['室', '厅'],
        'area': ['平米'],
        'towards': ['东', '南', '西', '北'],
        'decorate': ['精装', '简装', '毛坯'],
        'storey': ['层'],
        'period': ['年'],
        'categorie': ['板塔结合', '板楼', '塔楼'] 
    }
    res = {}
    for detail in details:
        for key, values in features.items():
            for value in values:
                if value in detail:
                    res[key] = detail
    return res

def extract(html_code):
    """将 html 中的关键信息解析并存入字典"""
    try:
        root = etree.HTML(html_code)
    except Exception:
        return None
    li_list = root.xpath('//ul[@class="sellListContent"]/li')
    if not li_list:
        return None

    infos = []
    for li in li_list:
        # 获取标题
        title = li.xpath('./div[@class="info clear"]/div[@class="title"]/a/text()')
        title = title[0] if title else None

        # 获取地址
        location = li.xpath('./div[@class="info clear"]/div[@class="flood"]/div[@class="positionInfo"]/a/text()')
        location = ', '.join(location)

        # 获取房屋细节
        details = li.xpath('./div[@class="info clear"]/div[@class="address"]/div/text()')
        details = details[0].split(' | ') if details else None

        # 获取总价
        total_price = li.xpath('./div[@class="info clear"]/div[@class="priceInfo"]/div/span/text()')
        total_price = total_price[0] + ' 万' if total_price else None

        # 获取单价
        unit_price = li.xpath('./div[@class="info clear"]/div[@class="priceInfo"]/div[@class="unitPrice"]/@data-price')
        unit_price = unit_price[0] + ' 元' if unit_price else None

        # 获取图片 url
        image_url = li.xpath('./a[@class="noresultRecommend img LOGCLICKDATA"]/img[@class="lj-lazy"]/@data-original')
        image_url = image_url[0] if image_url else None
        
        # 获取跳转链接
        jump_link = li.xpath('./div[@class="info clear"]/div[@class="title"]/a/@href')
        jump_link = jump_link[0] if jump_link else None

        infos.append({
            'title': title,
            'location' : location,
            'details': categorise(details),
            'price': {
                'total_price': total_price,
                'unit_price': unit_price 
            },
            'image': image_url,
            'link': jump_link
        })
    return infos

def filtrate(data: str) -> str:
    """过滤非 GBK 编码字符"""
    result = ''
    for char in data:
        try:
            char.encode('GBK')
            result += char
        except UnicodeEncodeError:
            continue
    return result

def local_image(url: str) -> str:
    """将图片保存到本地, 返回本地图片地址"""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': f'https://{city}.lianjia.com/ershoufang/'
    }
    try:
        response = requests.get(url=url, headers=headers, timeout=3)
        match = re.search(r'https://image1\.ljcdn\.com/110000-inspection/(.+?)\.\d+x\d+\.jpg$', url)
        if match:
            file_name = match.group(1)
            file_path = os.path.join('AppData', 'image', file_name)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return 'file://' + os.path.abspath(file_path)
        else:
            return None
    except Exception:
        time.sleep(random.random())
        return local_image(url)

if __name__ == '__main__':
    # 获取爬取范围
    city_chinese = input('请输入城市:')
    if city_chinese not in CITY_CODE:
        print('链家暂未提供该城市相关信息.')
        exit(0)
    city = CITY_CODE[city_chinese]
    left, right = map(int, input('请输入页数范围:').split())
    
    infos = []
    for page in range(left, right + 1):
        # 设定页面 url 和请求 headers
        url = f'https://{city}.lianjia.com/ershoufang/pg{page}/'
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': f'https://{city}.lianjia.com/ershoufang/pg{page}/'
        }
        # 不断发起请求, 直到解析成功
        # 因为链家正常来说会返回 html, 但小概率会返回 JavaScript
        info = None
        while not info:
            html_code = get_html(url, headers)
            info = extract(html_code)
        infos.extend(info)
        print(f'page {page} completed.')

    print('Saving images...')
    os.startfile(os.path.join('AppData', 'image'))
    for info in infos:
        info['image'] = local_image(info['image'])

    # 将数据写入到 json 文件
    print('Saving to json...')
    with open(f'./AppData/information/{city_chinese}_{left}-{right}.json', 'w', encoding='utf-8') as file:
        json.dump(fp=file, obj=infos, ensure_ascii=False, indent=4)
    
    # 将数据写入到 csv 文件
    print('Saving to csv...')
    table = [['title', 'location', 'configuration', 'area', 'towards', 'decorate', 'storey', 'period', 'categorie', 'total_price', 'unit_price', 'image', 'link']]
    for info in infos:
        line = [None] * 13
        for i, key in enumerate(table[0][:2]):
            if key in info:
                line[i] = info[key]
        for i, key in enumerate(table[0][2:9]):
            if key in info['details']:
                line[i + 2] = info['details'][key]
        for i, key in enumerate(table[0][9:11]):
            if key in info['price']:
                line[i + 9] = info['price'][key]
        for i, key in enumerate(table[0][11:]):
            if key in info:
                line[i + 11] = info[key]

        for i, key in enumerate(line):
            if key is not None:
                line[i] = filtrate(key)

        table.append(line)

    table[0] = ['标题', '地址', '户型', '面积', '朝向', '装修情况', '层数', '建造时间', '楼型', '总价', '每平米单价', '图片', '详情链接']
    with open(f'./AppData/information/{city_chinese}_{left}-{right}.csv', 'w', encoding='GBK') as file:
        writer = csv.writer(file)
        writer.writerows(table)