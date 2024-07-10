import requests
import re
import os
import multiprocessing
import time
import random
from chardet.universaldetector import UniversalDetector
import chardet
import io
import sys
from fake_useragent import UserAgent

ua = UserAgent()
headers = {'USER-Agent': UserAgent().chrome}


def _1_get_url(page, pic_type):
    if pic_type == '1':
        url = 'https://t66y.com/thread0806.php?fid=7&search=&page=' + page  # 技术交流
    if pic_type == '2':
        url = 'https://t66y.com/thread0806.php?fid=8&search=&page=' + page  # 新時代的我們
    if pic_type == '3':
        url = 'https://t66y.com/thread0806.php?fid=16&search=&page=' + page  # 達蓋爾的旗幟

    res = requests.get(url, headers=headers, verify=False)
    code = re.findall('charset=(.*)\"', res.text)[0]
    if not code:
        code = chardet.detect(res.content)['encoding']
    res.encoding = code
    text = res.text
    a = re.findall('a href="(.*?)html"', text)
    return a


def baocun(url, name):
    n = re.findall('(.*?)[P\-]', name)
    root = 'pic' + os.sep + n[0] + os.sep
    try:
        os.makedirs(root)
    except:
        pass
    if url[-4] == '.':
        path = root + name + url[-4:]
    if url[-5] == '.':
        path = root + name + url[-5:]
    if not os.path.exists(root):
        os.mkdir(root)
    if not os.path.exists(path):
        r = requests.get(url)
        r.raise_for_status()
        with open(path, 'wb') as f:
            f.write(r.content)
            print('爬取成功')


def getimgscl(url, name='default'):
    count = 0
    res = requests.get(url, headers=headers)
    code = re.findall('charset=(.*)\"', res.text)[0]
    if not code:
        code = chardet.detect(res.content)['encoding']
    res.encoding = code
    text = res.text
    a = re.findall('ess-data=\'(.*?)\'', text)
    title1 = re.findall('<title>(.*?)\|', text)
    title = re.findall('(.*?)P', title1[0])[0]
    print(title)
    print(code, url)
    if title:
        name = title
    pic_list = []
    pic_list.append(title)
    for i in a:
        pic_list.append(i)
    return pic_list


def save_pic(url, count, title):
    if '.gif' in url:
        extension = '.gif'
    elif '.png' in url:
        extension = '.png'
    elif '.jpg' in url:
        extension = '.jpg'
    elif '.jpeg' in url:
        extension = '.jpeg'
    else:
        extension = re.findall('.*(\..*)', url)[-1]
    try:
        os.makedirs('pic' + os.sep + title)
    except:
        pass
    file_name = ("pic" + os.sep + title + os.sep + title + str(count + 1) + extension)
    file_name = re.sub(re.compile('[/\:*?"<>|]'), '', file_name)
    res = requests.get(url)
    print(len(res.content) // 1024 // 1024, url)
    time.sleep(1)  # 增加延迟，确保文件写入完成
    with open(file_name, 'wb') as f:
        f.write(res.content)
    print('保存成功')


def process_download(save_pic, url_list, title):
    processes = []
    start = time.time()
    for i in range(len(url_list)):
        p = multiprocessing.Process(target=save_pic, args=[url_list[i], i, title])
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    end = time.time()
    print('多进程总耗时：%r' % (end - start))


if __name__ == '__main__':
    types = ['1', '2', '3']
    pic_type = random.choice(types)
    page1 = '5'
    page2 = '6'
    crawled = []
    try:
        with open('已爬取草榴p.log', 'r') as file:
            for line in file:
                crawled.append(line[:-1])
    except:
        pass
    for page in range(int(page1), int(page2) + 1):
        a = _1_get_url(str(page), pic_type)
        for i in a:
            if i not in crawled:
                try:
                    with open('已爬取草榴p.log', 'a') as file:
                        file.write(i + '\n')
                    imgs = getimgscl('https://t66y.com/' + i + 'html')
                    title = imgs[0]
                    print(title)
                    del imgs[0]
                    process_download(save_pic, imgs, title)
                except:
                    print('下载失败')
            else:
                print('已爬取，跳过', i)
