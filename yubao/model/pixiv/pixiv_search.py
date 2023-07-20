import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from yubao.util import aiorequest
from yubao.config import Config
config = Config().read_config()

async def search_pic(keyword, popular, r18):
    url = f"{config['rsshub_base']}/pixiv/search/{keyword}/{popular}/{r18}"
    illus = []
    res = await aiorequest.get(url)
    root = ET.XML(await res.text)
    channel = root.find('channel')
    topic = channel.find('title')
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
    return illus