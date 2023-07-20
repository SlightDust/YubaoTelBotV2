
# 需要在model目录下新建一个名字为插件名称的目录，然后在目录下新建__init__.py文件，将该文件的内容复制到__init__.py中

# 系统库引用
import random
import json
import asyncio

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao import extendChat
from yubao.util.logger import new_logger
# from yubao.util.imageProcess import Image2BufferedReader

from yubao.config import Config
config = Config().read_config()

from .pixiv_search import search_pic

bot = yubao.get_bot()
model_name = "pixiv搜索"  # 在此处定义插件名称

delete_delay = 30
helptext = f"pixiv搜索 关键词 -参数\n参数包括：\n-r18 仅搜索r-18涩图\n-safe：仅搜索非r-18涩图\n-any：不过滤r18（默认）\n-popular：按热度搜索\n-any：搜索最新结果（默认）"

@bot.command(r"^帮助pixiv搜索$")
async def help_pixiv(chat:Chat, match):  # 需要修改为插件名
    await chat.reply(helptext)


@bot.command(r"^pixiv搜索\s+(?P<keyword>\S+)(\s+(?P<args>.*))?")
async def pixiv(chat:Chat, match):  # 需要修改为插件名
    chat.__class__ = extendChat
    logger = new_logger(model_name)
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 {model_name} 消息: {chat.message}')
    if 'private' in chat.type:
        chat.reply("请在群聊中使用该功能~")
        return
    ###################### 下面开始插件主体 #####################
    keyword = match.group('keyword')
    sent_msg = await chat.reply(f"正在搜索{keyword}……")
    to_del_mid = sent_msg.get("result").get("message_id")
    r18 = "any"
    popular = "any"
    try:
        if "-r18" in match.group('args'):
            r18 = "r18"
        elif "-safe" in match.group('args'):
            r18 = "safe"
        if "-popular" in match.group('args'):
            popular = "popular"
    except TypeError:  # no args
        pass
    try:
        illus = await search_pic(keyword=keyword,popular=popular,r18=r18)
    except:
        await chat.delete_message(message_id=to_del_mid)
        await chat.send_text("搜索失败，请稍后再试。\n@pipichen_nya 看日志")
        return 
    total_count = len(illus)
    msg = f"搜索到{total_count}个结果，随机发送1个\n"
    choose = random.choice(illus)

    inlinekeyboardmarkup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': [
            [{'type': 'InlineKeyboardButton',
            'text': 'pixiv搜索帮助',
            'callback_data': f'button_help_pixiv'}]
            ]
        }
    
    msg += f"标题：{choose.get('title')}\n作者：{choose.get('author')}\n阅读量：{choose.get('read')}\n收藏：{choose.get('favour')}\n发布时间：{choose.get('pubDate')}\npixiv链接：{choose.get('link')}"
    # await chat.send_text(msg, reply_markup=json.dumps(inlinekeyboardmarkup), no_webpage=True)
    try:
        await chat.send_photo(photo=choose.get('pic0_url'), caption=msg)
    except:
        await chat.send_text("下载图片失败，将尝试直接发送文本")
        await chat.send_text(msg, no_webpage=True)
    await chat.delete_message(message_id=to_del_mid)
    sent_pixiv_msg = await chat.send_text("点击获取pixiv搜图帮助", reply_markup=json.dumps(inlinekeyboardmarkup))
    to_del_pixiv_mid = sent_pixiv_msg.get("result").get("message_id")
    await asyncio.sleep(8)
    await chat.delete_message(message_id=to_del_pixiv_mid)

@bot.callback(r'button_help_pixiv')
async def button_help_pixiv(chat, cq, match):
    sent_msg = await bot.send_message(chat_id=cq.src.get('message').get('chat').get('id'), text=helptext+f"\n{delete_delay}秒后自动撤回该帮助")
    to_del_mid = sent_msg.get("result").get("message_id")
    await asyncio.sleep(delete_delay)
    await chat.delete_message(message_id=to_del_mid)  # 撤回反馈互动,防止刷屏
