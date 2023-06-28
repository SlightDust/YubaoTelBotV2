# 系统库引用
import os
import json

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao.config import __bot__ as profile
from yubao.util.logger import new_logger
from yubao.util.make_at import at_sender

bot = yubao.get_bot()

help_file = os.path.join(os.path.dirname(__file__), 'help.txt')

@bot.command(r"^/start(@YubaoTelBot)?$")
async def start(chat:Chat, match):
    logger = new_logger("start")
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 /start 命令')
    text = "Hello! This is YubaoTelBotV2 powered by aiotg-proxy!"
    await bot.send_message(chat_id=chat.id, text=text)

@bot.command(r"^/test(@YubaoTelBot)?$")
async def test(chat:Chat, match):
    logger = new_logger("test")
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 /test 命令')
    text = "This is a test message."
    await bot.send_message(chat_id=chat.id, text=text)

@bot.command(r"^/help(@YubaoTelBot)?$")
async def help(chat:Chat, match):
    logger = new_logger("help")
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 /help 命令')
    with open(help_file, 'r', encoding='utf-8') as f:
        help_txt = f.read()
    await bot.send_message(chat_id=chat.id, text=help_txt)

@bot.command("atme")
async def at_test(chat:Chat, match):
    logger = new_logger("atme")
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 atme 命令: {chat.message}')
    text, at = await at_sender(chat)
    await chat.send_text(text=text, entities=at)
    return 
    cid = chat.id
    uid = chat.message.get("from").get('id')
    uname = chat.message.get('from').get('username')
    ufstname = chat.message.get('from').get('first_name')
    # print(uid, uname, ufstname)
    if uname is not None:
        # 发送者设置了username，优先以@username的形式创建mention
        at = f"[{{'offset': 0, 'length': {1+len(uname)}, 'type':'mention', }}]"
        await chat.send_text(text=f'@{uname}')
    else:
        # 发送者未设置username，创建text_mention
        at = [
            {'offset': 0, 
             'length': len(ufstname), 
             'type': 'text_mention', 
             'user':{'id': uid, 
                     'is_bot': False, 
                     'first_name': ufstname
                     }
            }]
        await chat.send_text(text=f'{ufstname}', entities=json.dumps(at, ensure_ascii=False))


    # at = f"[\{'offset': 0, 'length': {}, 'type':'text_mention', \}]"