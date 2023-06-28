# 系统库引用
import os

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao.config import __bot__ as profile
from yubao.util.logger import new_logger

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