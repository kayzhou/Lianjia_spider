import requests
from bs4 import BeautifulSoup
import os
import re
import json
import time

p = re.compile('<[^>]+>')

def get_house(url, out_name):
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    # soup.title
    bo = soup.body
    data = {}
    data['url'] = url
    # html body div.sellDetailHeader div.title-wrapper div.content div.title h1.main
    result = bo.find('div', 'sellDetailHeader').find('div', 'title-wrapper').find('div', 'content').find('div', 'title').find('h1', 'main')
    data['title'] = result.get_text()

    result = bo.find('div', 'overview').find('div', 'content').find('div', 'price').find('span', 'total')
    name = result['class'][0]
    value = result.string
    # print(name, value)
    data[name] = value

    result = bo.find('div', 'overview').find('div', 'content').find('div', 'price').find('span', 'unit')
    name = result['class'][0]
    value = result.string
    # print(name, value)
    data[name] = value

    # html body div.overview div.content div.price div.text div.unitPrice span.unitPriceValue
    result = bo.find('div', 'overview').find('div', 'content').find('div', 'price').find('div', 'text').find('div', 'unitPrice').find('span', 'unitPriceValue')
    name = result['class'][0]
    value = result.contents[0]
    # print(name, value)
    data[name] = value

    # html body div.overview div.content div.houseInfo
    result = bo.find('div', 'overview').find('div', 'content').find('div', 'houseInfo')
    # print(result.contents)
    for r in result.contents:
        name = r['class'][0]
        data[name + '_mainInfo'] = r.find_all('div')[0].string
        data[name + '_subInfo'] = r.find_all('div')[1].string

    # html body div.overview div.content div.aroundInfo

    # html body div.overview div.content div.aroundInfo div.communityName a.info
    result = bo.find('div', 'overview').find('div', 'content').find('div', 'aroundInfo').find('div', 'communityName').find('a', 'info')
    data['communityName'] = result.string

    # html body div.overview div.content div.aroundInfo div.areaName span.info
    result = bo.find('div', 'overview').find('div', 'content').find('div', 'aroundInfo').find('div', 'areaName').find('span', 'info')
    # print(result)
    value = p.sub("", str(result)).replace('\xa0', ' ')
    data['areaName'] = value

    # html body div.overview div.content div.aroundInfo div.visitTime span.info
    result = bo.find('div', 'overview').find('div', 'content').find('div', 'aroundInfo').find('div', 'visitTime').find('span', 'info')
    data['visitTime'] = result.string

    # html body div.overview div.content div.aroundInfo div.houseRecord span.info
    result = bo.find('div', 'overview').find('div', 'content').find('div', 'aroundInfo').find('div', 'houseRecord').find('span', 'info')
    # print(result)
    data['_id'] = result.get_text()[:-2]

    # html body div.m-content div.box-l div#introduction.newwrap.baseinform div div.introContent div.base div.content ul
    box_1 = bo.find('div', 'm-content').find('div', 'box-l').find(id='introduction').find('div').find('div', 'introContent')
    _box_1 = box_1.find('div', 'base').find('div', 'content').find('ul').find_all('li')
    for box in _box_1:
        name = box.find('span').string
        data[box.find('span').string] = box.get_text()[len(name):]
    # print(data)
    # print(box_1)

    # html body div.m-content div.box-l div#introduction.newwrap.baseinform div div.introContent div.transaction div.content ul
    _box_2 = box_1.find('div', 'transaction').find('div', 'content').find('ul').find_all('li')

    for box in _box_2:
    #     print(box)
        name = box.find('span').string
        data[box.find('span').string] = box.get_text()[len(name):]


    # html body div.m-content div.box-l div.newwrap.baseinform div.introContent.showbasemore
    # html body div.m-content div.box-l div.newwrap.baseinform div.introContent.showbasemore div.baseattribute.clear

    result = bo.find('div', 'm-content').find('div', 'box-l').find_all('div')[20].get_text()
    data['房源标签'] = result.replace('\n', ' ').strip()

    results = bo.find('div', 'm-content').find('div', 'box-l').find_all('div')[17].find_all('div', 'baseattribute clear')
    # print(results)

    for result in results:
        name = result.find('div', 'name').get_text().strip()
        value = result.find('div', 'content').get_text().strip()
        data[name] = value

    # html body div.m-content div.box-l div.newwrap div#layout.layout-wrapper div.layout div.content div.des div.info div.list div#infoList
    results = bo.find('div', 'm-content').find('div', 'box-l').find('div', 'layout-wrapper').find('div', 'layout').find('div', 'content').find('div', 'des').find('div', 'info').find('div', 'list').find_all('div', 'row')
    # [45].find_all('div')[2].find_all('div')[0].find('div', 'list').find_all('div', 'row')
    huxing = []
    for result in results:
        huxing.append(result.get_text().strip().split('\n'))
    data['户型分间'] = huxing
    # print(huxing)
    # html body script
    results = bo.find_all('script')[21]
    # print(results.get_text())
    # for line in results.get_text().split('\n'):
    #     print(i, line)
    #     i += 1
    js = results.get_text()
    start = js.find('init(')
    end = js.find('images: [{')

    # js.find_last
    js = js[start+5: end].replace('\n', '').split(' ')
    for t in js:
        if ':' not in t:
            continue
        key = t.split(':')[0]
        value = t[t.find(':') + 1:-1].replace('true', 'True').replace('false', 'False')
        if value == '':
            continue
        # print(value)
        if value == "'true'":
            value = 'True'
        elif value == "'false'":
            value = 'False'
        try:
            value = eval(value)
        except:
            # print('解析失败 ...')
            continue
        data[key] = value

    json.dump(data, open(out_name, 'w'), indent=2, ensure_ascii=False)



for i in range(2, 10000):
    home = requests.get("https://bj.lianjia.com/ershoufang/pg{}".format(i)).text
    home = BeautifulSoup(home, "lxml")

    # html body div.content div.leftContent ul.sellListContent li.clear div.info.clear div.title a
    my_houses = home.body.find('div', 'content').find('div', 'leftContent').find('ul', 'sellListContent').find_all('li', 'clear')

    for house in my_houses:
        url = house.find('a').get('href')
        print(url)
        time.sleep(1)
        _id = url.split('/')[-1][:-5]
        if not os.path.exists('data/{}.json'.format(_id)):
            try:
                get_house(url, 'data/{}.json'.format(_id))
            except:
                print('Error ->', url)
