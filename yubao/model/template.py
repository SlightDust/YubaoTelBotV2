
# 需要在model目录下新建一个名字为插件名称的目录，然后在目录下新建__init__.py文件，将该文件的内容复制到__init__.py中

# 系统库引用

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
from yubao import extendChat
from yubao.util.logger import new_logger
# from yubao.util.imageProcess import Image2BufferedReader

from yubao.config import Config
config = Config().read_config()


bot = yubao.get_bot()
model_name = ""  # 在此处定义插件名称

@bot.command(r"这里是指令的正则表达式")
async def model_name(chat:Chat, match):  # 需要修改为插件名
    chat.__class__ = extendChat
    logger = new_logger(model_name)
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 {model_name} 消息: {chat.message}')
    if 'private' in chat.type:
        chat.reply("请在群聊中使用该功能~")
        return
    ###################### 下面开始插件主体 #####################