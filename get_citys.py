import time
import random
import json
import re
import requests
from lxml import etree

with open('./AppData/USER_AGENTS.json', 'r', encoding='UTF-8') as file:
    USER_AGENTS = json.load(file)
URL = 'https://www.lianjia.com/city/'
headers = {
    'User-Agent': '',
    'Referer': 'https://cs.lianjia.com/'
}

def get_html() -> str:
    headers['User-Agent'] = random.choice(USER_AGENTS)
    try:
        response = requests.get(url=URL, headers=headers, timeout=3)
        if not response:
            raise Exception()
    except Exception:
        time.sleep(random.random())
        return get_html()
    else:
        return response.text

def extract(html: str) -> dict:
    try:
        root = etree.HTML(html)
    except Exception:
        return None
    city_list = root.xpath('//div[@class="city_province"]/ul/li')
    city_code = dict()
    for city in city_list:
        name = city.xpath('./a/text()')[0]
        url = city.xpath('./a/@href')[0]
        match = re.search(r'https://([a-z]+).lianjia.com/', url)
        if match:
            code = match.group(1)
            city_code[str(name)] = str(code)
    return city_code

if __name__ == '__main__':
    city_code = None
    while not city_code:
        city_code = extract(get_html())
    with open('./AppData/CITY_CODE.json', 'w', encoding='UTF-8') as file:
        json.dump(fp=file, obj=city_code, ensure_ascii=False, indent=4)