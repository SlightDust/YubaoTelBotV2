'''
    from: pcrbot/ai_setu
'''
# 系统库引用

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
import yubao.util.aiorequest
from yubao.util.logger import new_logger
logger = new_logger("echo_yubao")
bot = yubao.get_bot()

from . import until


@bot.command(r"^AI绘图|^ai绘图|^SD绘图|^sd绘图(.+)")
async def text2img_sd(chat:Chat, match):
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 ai_setu 消息: {chat.message}')
    # if not flmt.check(uid):
    #     await bot.send(ev, f'您冲的太快了,{round(flmt.left_time(uid))}秒后再来吧~', at_sender=True)
    #     return 
    mid = chat.message.get('message_id')
    sent_msg = await chat.send_text(text="少女绘图中……")  # 反馈互动
    to_del_mid = sent_msg.get("result").get("message_id")

    # flmt.start_cd(uid)
    tags = match.group(0)
    tags.replace("ai绘图","").replace("AI绘图","").replace("sd绘图","").replace("SD绘图","")

    tag_dict,error_msg,tags_guolv = await until.process_tags(chat.id,chat.message.get('from').get('id'),tags) #tags处理过程
    if len(error_msg):
        await chat.send_text(text=f"已报错：{error_msg}")
    if len(tags_guolv):
        await chat.send_text(text=f"已过滤：{tags_guolv}")
    result_msg,error_msg = await until.get_imgdata_sd(tag_dict,way=0)
    if len(error_msg):
        await chat.send_text(text=f"已报错：{error_msg}", at_sender=True)
        return
    try:
        await chat.delete_message(message_id=to_del_mid)  # 撤回反馈互动,防止刷屏
    except:
        await chat.send_text(text=f"请给bot管理员以解锁全部功能")
    # print(result_msg)
    # await chat.send_photo(photo=open(result_msg, 'rb'))
    await bot.send_photo(chat_id=chat.id, photo=open(result_msg, 'rb'), reply_to_message_id=mid)