# 系统库引用
from PIL import Image

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao import extendChat
from yubao.util.logger import new_logger
from yubao.util.imageProcess import Image2BufferedReader

from .generator import genImage

bot = yubao.get_bot()

@bot.command(r"^5kcy (?P<line1>.+)[\|丨 ](?P<line2>.+)$")
async def _5kcy(chat:Chat, match):
    chat.__class__ = extendChat
    logger = new_logger("5kcy")
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 5kcy 消息: {chat.message}')
    line1 = match.group("line1")
    line2 = match.group("line2")
    try:
        upper = line1
        downer = line2
        img = genImage(word_a=upper, word_b=downer)
        img = await Image2BufferedReader(img)
        await chat.send_photo(photo = img)
    except OSError:
        await chat.send_text(text='生成失败……请检查字体文件设置是否正确')
    except:
        await chat.send_text(text='生成失败……请检查命令格式是否正确')