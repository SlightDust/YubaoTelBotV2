# 系统库引用
import sys, os
sys.path.append(os.getcwd())

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao.config import Config
from yubao.util.logger import new_logger
config = Config().read_config()

bot = yubao.init(token=config['token'], proxy=config['proxy'], default_in_groups=True)


@bot.command(r"/echo (.+)")
async def echo(chat, match):
    return await chat.reply(match.group(1))

from yubao.model import echo_yubao
from yubao.model import command
from yubao.model import setu
from yubao.model import ai_setu
from yubao.model import fortune_yubao
from yubao.model import login_bonus

@bot.default
def unknow(chat:Chat, message):
    logger = new_logger("unknow")
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 undefined 消息: {chat.message}')




bot.run()

