import requests
import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

config={"rsshub_base":"https://rsshub.app"}

pattern = r"^pixiv搜索\s+(?P<keyword>\S+)\s+(?P<args>.*)"
meirei = "pixiv搜索 凯露 -r18 -popular"
remsg = re.search(pattern,meirei)

keyword = remsg.group('keyword')
r18 = "any"

if "-r18" in remsg.group('args'):
    r18 = "r18"
elif "-safe" in remsg.group('args'):
    r18 = "safe"

if "-popular" in remsg.group('args'):
    popular = "popular"

illus = []

url = f"{config['rsshub_base']}/pixiv/search/{keyword}/{popular}/{r18}"
print(url)

res = requests.get(url)
# res.encoding = 'utf-8'
root = ET.XML(res.text)
channel = root.find('channel')
title = channel.find('title')
for item in channel.iter(tag="item"):
    pattern = r"画师：(?P<author>.+) - 阅览数：(?P<read>\d+) - 收藏数：(?P<favour>\d+)"
    reres = re.search(pattern=pattern, string=item.find('description').text)
    pic0_url = re.search(r"src=\"(?P<picurl>.*?)\"", string=item.find('description').text).group('picurl')
    one = {
        "title": item.find('title').text,
        "author": item.find('author').text,
        "read": reres.group('read'),
        "favour": reres.group('favour'),
        "pubDate": item.find('pubDate').text,
        "link": item.find('link').text,
        "pic0_url": pic0_url
        }
    illus.append(one)
    print(one)
