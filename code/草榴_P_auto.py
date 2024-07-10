import requests
import re
import os
import multiprocessing
import time
import random
from chardet.universaldetector import UniversalDetector
from fake_useragent import UserAgent

ua = UserAgent()
headers = {'USER-Agent': ua.chrome}


def _1_get_url(page, pic_type):
    if pic_type == '1':
        url = 'https://t66y.com/thread0806.php?fid=7&search=&page=' + page  # 技术交流
    elif pic_type == '2':
        url = 'https://t66y.com/thread0806.php?fid=8&search=&page=' + page  # 新時代的我們
    elif pic_type == '3':
        url = 'https://t66y.com/thread0806.php?fid=16&search=&page=' + page  # 達蓋爾的旗幟

    res = requests.get(url, headers=headers, verify=False)
    code = re.findall('charset=(.*)\"', res.text)[0]
    if not code:
        code = chardet.detect(res.content)['encoding']
    res.encoding = code
    text = res.text
    a = re.findall('a href="(.*?)html"', text)
    return a


def save_pic(url, count, title):
    try:
        os.makedirs('pic' + os.sep + title)
    except FileExistsError:
        pass  # 如果文件夹已存在，则继续

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

    file_name = f"pic{os.sep}{title}{os.sep}{title}_{count + 1}{extension}"
    file_name = re.sub(r'[\\/:*?"<>|]', '', file_name)  # 清理非法字符
    try:
        res = requests.get(url, headers=headers)
        print(len(res.content) // 1024 // 1024, url)
        time.sleep(1)  # 增加延迟，确保文件写入完成
        with open(file_name, 'wb') as f:
            f.write(res.content)
        print('保存成功')
    except Exception as e:
        print(f'保存失败: {e}')


def process_download(save_pic, url_list, title):
    processes = []
    start = time.time()
    for i, url in enumerate(url_list):
        p = multiprocessing.Process(target=save_pic, args=(url, i, title))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    end = time.time()
    print(f'多进程总耗时：{end - start}秒')


if __name__ == '__main__':
    types = ['1', '2', '3']
    pic_type = random.choice(types)
    page1 = '5'
    page2 = '6'
    crawled = []
    try:
        with open('已爬取草榴p.log', 'r') as file:
            crawled = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        pass

    for page in range(int(page1), int(page2) + 1):
        urls = _1_get_url(str(page), pic_type)
        for url in urls:
            if url not in crawled:
                try:
                    with open('已爬取草榴p.log', 'a') as file:
                        file.write(url + '\n')
                    imgs = getimgscl('https://t66y.com/' + url + 'html')
                    title = imgs[0]
                    print(title)
                    del imgs[0]
                    process_download(save_pic, imgs, title)
                except Exception as e:
                    print(f'下载失败: {e}')
            else:
                print('已爬取，跳过', url)
