# 系统库引用
import random

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao.config import __bot__ as profile
from yubao.util.logger import new_logger
logger = new_logger("echo_yubao")
bot = yubao.get_bot()

# ('域宝','域宝？','域宝?','域宝！','域宝!','@域宝','@域宝 ','域寶','域寶？','域寶！','>域寶?','域寶!')

# 消息处理函数
@bot.command(r"^域宝$")
async def echo_yubao(chat:Chat, match):
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 echo_yubao消息: {chat.message}')
    texts = profile.yubao_say.copy()
    await chat.send_text(text=random.choice(texts))