'''
    from: pcrbot/setu_renew
'''
# 系统库引用
import re
import aiohttp
import traceback
import json

# 三方库引用
from aiotg import Chat
from aiotg.bot import BotApiError

# 自目录引用
import yubao
import yubao.util.aiorequest
from yubao.util.logger import new_logger
logger = new_logger("echo_yubao")
bot = yubao.get_bot()
from yubao.config import Config
config = Config().read_config()

logger = new_logger("setu")

@bot.command(r'^[色涩瑟][图圖]|不够[色涩瑟]|[来來发發给給]((?P<num>\d+)|(?:.*))[张張个個幅点點份丶](?P<keyword>.*?)[色涩瑟][图圖]$')
async def setu(chat:Chat, match):
    sent_msg = await chat.reply(text="正在搜索，请稍候……")
    to_del_mid = sent_msg.get("result").get("message_id")
    num = match.group("num")
    num = 1 if num is None else num
    keyword = match.group("keyword")
    if keyword == "域宝":
        await chat.reply(text="域宝没有色图哦")
        return 
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 setu 消息: {chat.message}')
    images = await get_random_lolicon_setu_online(r18=2,keyword=keyword,num=num)
    await chat.delete_message(message_id=to_del_mid)
    if len(images)==0:
        await chat.reply(text=f"没有找到{keyword}的色图")
    for image in images:
        tags = ''.join(i+', ' for i in image['tags'][0:-1])+' '+image['tags'][-1] if len(image['tags'])>1 else image['tags']
        msg = f"pid: {image['id']}\ntitle: 「{image['title']}」\n作者: 「{image['author']}」\ntags: {tags}\nurl: {image['url']}"
        if ("R-18" in tags) and ("private" not in chat.type):
            # R-18图片单独发送
            # chat.send_text("R-18图片已通过私聊发送")
            try:
                r18msg = await bot.send_message(chat_id=chat.message.get('from').get('id'),text=msg)
                sent_chatid = chat.message.get('from').get('id')
                sent_messageid = r18msg.get('result').get('message_id')
                inlinekeyboardmarkup = {
                    'type': 'InlineKeyboardMarkup',
                    'inline_keyboard': [
                        [{'type': 'InlineKeyboardButton',
                        'text': '坚持访问',
                        'callback_data': f'showr18pic-{sent_chatid}-{sent_messageid}'}]
                        ]
                    }
                await chat.send_text(f'@{chat.message.get("from").get("username")} R-18图片已通过私聊发送。\n任何人点击按钮可接收私聊消息。', reply_markup=json.dumps(inlinekeyboardmarkup))
            except BotApiError as e:    # 未认证bot
                print(e.args)
                if "bot can't initiate conversation with a user" in str(e.args):
                    await chat.reply(f'@{chat.message.get("from").get("username")} R-18图片私聊发送失败。请先私聊域宝并发送/start后再试。')
                elif "bot was blocked by the user" in str(e.args): 
                    await chat.reply(f'@{chat.message.get("from").get("username")} 您屏蔽了域宝的私聊消息。R-18图片发送失败。')
                else:
                    await chat.reply(f'@{chat.message.get("from").get("username")} R-18图片私聊发送失败: \n{e}')
                pass
        else:
            await chat.send_text(text=msg)

@bot.callback(r'^showr18pic-(.+?)-(.+)')
async def showr18pic(chat, cq, match):
    chat_id = cq.src.get('from').get('id')
    from_chat_id = match.group(1)
    message_id = match.group(2)
    # print(chat_id, from_chat_id, message_id)
    # print(cq.src)
    await bot.copy_message(chat_id, from_chat_id, message_id)
    await bot.send_message(chat_id=cq.src.get('message').get('chat').get('id'),text=f"@{cq.src.get('from').get('username')} 您点击了按钮，私聊请查收~", reply_to_message_id=cq.src.get('message').get('message_id'))
    

def generate_image_struct():
    return {
        'id': 0,
        'url': '',
        'title': '',
        'author': '',
        'tags': [],
        'r18': False,
        'data': None,
        'native': False,
    }

async def get_random_lolicon_setu_online(r18, keyword=None, num=1):
    '''ref: Hoshinobot setu_renew'''
    # await asyncio.sleep(10)
    image_list = []
    data = {}
    url = 'https://api.lolicon.app/setu/v2'
    params = {
        'r18': r18,
        'num': num,
        # 'proxy': '', 
    }
    if keyword:
        params['keyword'] = keyword
    thumb = True
    params['size'] = 'regular'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, proxy=config['proxy']) as resp:
                data = await resp.json(content_type='application/json')
    except Exception:
        traceback.print_exc()
        return image_list
    if 'error' not in data:
        return image_list
    if data['error'] != '':
        logger.error(f'[ERROR]lolicon api error,msg:{data["error"]}')
        return image_list
    for item in data['data']:
        image = generate_image_struct()
        image['id'] = item['pid']
        image['title'] = item['title']
        image['url'] = item['urls']['regular' if thumb else 'original']
        image['tags'] = item['tags']
        image['r18'] = item['r18']
        image['author'] = item['author']
        image_list.append(image)
    return image_list