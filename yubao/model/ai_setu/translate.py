import yubao.util.aiorequest as aiorequests
import uuid
import hashlib
import time
import yaml
from os.path import dirname, join

curpath = dirname(__file__) #当前路径
config_path = join(curpath,"config.yaml")
with open(config_path,encoding="utf-8") as f: #初始化法典
    config = yaml.safe_load(f)#读取配置文件

transway = config['way2trans']
if transway:
    url = config['baidu_url']
    app_id = config['baidu_app_id']
    app_key = config['baidu_app_key']
else:
    url = config['youdao_url']
    app_id = config['youdao_app_id']
    app_key = config['youdao_app_key']



async def youdaoTranslate(translate_text,way=1):
    '''
    :param translate_text: 待翻译的句子
    :param flag: 1:原句子翻译成英文；0:原句子翻译成中文
    :return: 返回翻译结果
    '''

    # 翻译文本生成sign前进行的处理
    input_text = ""

    # 当文本长度小于等于20时，取文本
    if (len(translate_text) <= 20):
        input_text = translate_text

    # 当文本长度大于20时，进行特殊处理
    elif (len(translate_text) > 20):
        input_text = translate_text[:10] + str(len(translate_text)) + translate_text[-10:]

    time_curtime = int(time.time())  # 秒级时间戳获取
    uu_id = uuid.uuid4()  # 随机生成的uuid数，为了每次都生成一个不重复的数。

    sign = hashlib.sha256(
        (app_id + input_text + str(uu_id) + str(time_curtime) + app_key).encode('utf-8')).hexdigest()  # sign生成

    data = {
        'q': translate_text,  # 翻译文本
        'appKey': app_id,  # 应用id
        'salt': uu_id,  # 随机生产的uuid码
        'sign': sign,  # 签名
        'signType': "v3",  # 签名类型，固定值
        'curtime': time_curtime,  # 秒级时间戳
    }
    if way:
        data['from'] = "zh-CHS"  # 译文语种
        data['to'] = "en"  # 译文语种
    else:
        data['from'] = "en"  # 译文语种
        data['to'] = "zh-CHS"  # 译文语种

    r = await aiorequests.get(url, params=data)  # 获取返回的json()内容
    r = await r.json()
    # print("翻译后的结果：" + r["translation"][0])  # 获取翻译内容
    return r["translation"][0]


async def baiduTranslate(translate_text:str,way=1) -> str:

    # pre
    if way:
        from_lang = 'zh'  # original language
        to_lang = 'en'  # target language
    else:
        from_lang = 'en'  # original language
        to_lang = 'zh'  # target language
    # get text to translate
    input_text = '这里是需要翻译的内容。'
    input_text = translate_text

    # Generate salt and sign
    uu_id = uuid.uuid4()
    sign = hashlib.md5((app_id + input_text + str(uu_id) + app_key).encode('utf-8')).hexdigest()

    # Build request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'appid': app_id,
        'q': input_text,
        'from': from_lang,
        'to': to_lang,
        'salt': uu_id,
        'sign': sign
    }

    # Send request
    r = await (await aiorequests.post(url, params=data, headers=headers)).json()

    # Show response
    return r["trans_result"][0]["dst"]


async def tag_trans(tags):
    for c in tags:
        if ('\u4e00' <= c <= '\u9fa5'):
            isChinese = True
            break
        else:
            isChinese = False
    if(isChinese):
        tags= (await baiduTranslate(tags)) if transway else (await youdaoTranslate(tags))
    return tags

async def txt_trans(tags,way=1):
    tags= (await baiduTranslate(tags,way)) if transway else (await youdaoTranslate(tags,way))
    return tags