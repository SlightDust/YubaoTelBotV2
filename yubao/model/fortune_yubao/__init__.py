# 系统库引用
import random
import json
import asyncio
# import pymysql
import datetime
import time
import os
from PIL import Image, ImageDraw, ImageFont
import json

# 三方库引用
from aiotg import Chat

# 自目录引用
import yubao
import yubao.util.aiorequest
from yubao.util.imageProcess import Image2BufferedReader
from yubao.util.logger import new_logger
logger = new_logger("fortune_yubao")
bot = yubao.get_bot()

# 数据库
# from yubao.config.fortune_yubao import (MySQL_host, MySQL_password, MySQL_port, MySQL_username, MySQL_database)

# 先纯抽签，不记数据库


font_path = './res/font/sakura.ttf'
img = Image.open('./res/img/fortune_yubao/fortune_small.png')

qianPool_path = os.path.join(os.path.dirname(__file__), 'qianPool.json')
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

async def draw_one(chuyi = 0):
    with open(qianPool_path, 'r', encoding='utf-8') as jsonfile:
        qian_pool = json.load(jsonfile)
    qian = random.choice(qian_pool)

    new_img = img.copy()
    draw = ImageDraw.Draw(new_img)
    # if chuyi == 0:
    #     text = random.choice(["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"])
    # else:
    #     text = random.choice(["大吉", "中吉", "小吉", "吉", "末吉"])  # 初詣只有吉签
    text = qian.get('签位')
    # 13: 50
    # 4: 120
    # y = -70/9 * x + 1360/9
    font_size = int(-80/9 * len(qian.get('签位')) + 1360/9)
    color = '#101010'
    image_font_center = (345, 170)
    ttfront = ImageFont.truetype(font_path, font_size)
    font_length = ttfront.getbbox(text)[2:4]
    draw.text((image_font_center[0] - font_length[0] / 2, image_font_center[1] - font_length[1] / 2),
              text, fill=color, font=ttfront)
    bufferd = await Image2BufferedReader(img=new_img)

    return [bufferd, qian.get('签位'), qian.get('签文'), qian.get('解签')]


@bot.command(r'^(域宝)?(抽签|运势|人品)$')
async def fortune(chat:Chat, match):
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 fortune_yubao 消息: {chat.message}')
    if 'private' in chat.type:
        chat.reply("请在群聊中使用该功能~")
        return
    with open (config_path, 'r', encoding='utf-8') as jsonfile:
        my_config = json.load(jsonfile)
    if my_config['disable'] == 1:
        await chat.reply("今天，命运掌握在自己的手里哦~")
        return
    gid = chat.id
    uid = chat.message.get("from").get('id')
    today = datetime.date.today()
    draw_result = await draw_one(chuyi = my_config['chuyi'])
    bufferedimage = draw_result[0] 
    qianwei = draw_result[1]
    qianwen = draw_result[2]
    jieqian = draw_result[3]
    millis = int(round(time.time() * 1000))
    txt = f"签位：{qianwei}\n签文：{qianwen}\n解签：{jieqian}"
    await chat.send_photo(photo = bufferedimage,caption=txt)


# @bot.command(r'^(域宝)?(抽签|运势|人品)$')
# async def fortune(chat:Chat, match):
#     logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 fortune_yubao 消息: {chat.message}')
#     if 'private' in chat.type:
#         chat.reply("请在群聊中使用该功能~")
#         return
#     with open (config_path, 'r', encoding='utf-8') as jsonfile:
#         my_config = json.load(jsonfile)
#     if my_config['disable'] == 1:
#         await chat.reply("今天，命运掌握在自己的手里哦~")
#         return
#     db = pymysql.connect(host=MySQL_host, user=MySQL_username, password=MySQL_password, database=MySQL_database)
#     cursor = db.cursor()
#     gid = chat.id
#     uid = chat.message.get("from").get('id')
#     today = datetime.date.today()
#     sql = f"select * from `抽签` where `群号` = '{gid}' and `QQ号` = '{uid}' and `日期` = '{today}'"
#     cursor.execute(sql)
#     data = cursor.fetchall()
#     if len(data) == 3:
#         # 已经抽了三次了
#         msg = f"你今天已经抽过三次了，抽签结果分别是【{data[0][3]}】，【{data[1][3]}】，【{data[2][3]}】，欢迎明天再来~"
#         await chat.reply(msg)
#     else:
#         # 没抽够三次
#         draw_result = draw_one(chuyi = my_config['chuyi'])
#         image = draw_result[0]
#         txt = draw_result[1]
#         millis = int(round(time.time() * 1000))
#         # pic = pic2b64(image)
#         # pic = MessageSegment.image(pic)
#         if random.random() < 0.05:
#             await chat.reply("凶带吉")
#         with open(qianPool_path, 'r', encoding='utf-8') as jsonfile:
#             qian_pool = json.load(jsonfile)
#         # at = MessageSegment({"type": "at","data": {"qq": uid}})
#         qian = random.choice(qian_pool)
#         while (("凶" in txt) and (("上" in qian['签位']) or "吉" in qian['签位'])) or (("吉" in txt) and (("下" in qian['签位']) or ("凶" in qian['签位']))):
#             qian = random.choice(qian_pool)
        
#         qianwei = qian['签位']
#         sql2 = f"insert into `抽签`(`群号`,`QQ号`,`日期`,`签`,`时间戳`,`签位`) values('{qid}','{uid}','{today}','{txt}','{millis}','{qianwei}')"
#         cursor.execute(sql2)
#         db.commit()
        
#         await bot.send(ev,f"{at} \n{pic}\n签位：{qian['签位']}\n签文：{qian['签文']}\n10秒后发送解签结果")
#         await asyncio.sleep(10)
#         await bot.send(ev,f"{at} \n签位：{qian['签位']}\n解签：{qian['解签']}")


# @sv.on_fullmatch(('抽签统计'))
# async def count(bot, ev: CQEvent):
#     db = pymysql.connect(host=MySQL_host, user=MySQL_username, password=MySQL_password, database=MySQL_database)
#     cursor = db.cursor()
#     qid = str(ev.group_id)
#     uid = str(ev.user_id)
#     sql = f"select `签`,count(*) as '数量' from `抽签` where `群号`={qid} and `QQ号`={uid} GROUP BY `签` order by `数量` desc"
#     cursor.execute(sql)
#     data = cursor.fetchall()
#     # print(data)
#     msg = "\n您的历史抽签结果统计如下：\n"
#     for i in data:
#         msg += i[0] + "：" + str(i[1]) + "次\n"
#     await bot.send(ev, msg, at_sender=True)
    

# @sucmd('/抽签模式')
# async def set_fortune_config(session: CommandSession):
#     bot = session.bot
#     ev = session.event
#     uid = session.event['user_id']
#     coffee = session.bot.config.SUPERUSERS[0]
#     if uid != coffee:
#         await bot.finish(ev,"您没有权限修改！")
#     received = session.current_arg
#     try:
#         config_item = received.split(' ')[0]
#         changeto = int(received.split(' ')[1])
#     except IndexError:
#         await bot.send(ev,"设置抽签模式，[chuyi|disable] [0|1]")
#         return
#     if changeto not in (0,1):
#         await bot.send(ev,"值错误！\n[chuyi|disable] [0|1]")
#         return
#     with open(config_path, 'r', encoding='utf-8') as jsonfile:
#         raw_set = json.load(jsonfile)
#     if config_item not in raw_set:
#         await bot.send(ev,"设置项错误\n[chuyi|disable] [0|1]")
#         return
#     # 没有问题
#     raw_set[config_item] = changeto
#     with open(config_path, 'w', encoding='utf-8') as jsonfile:
#         json.dump(raw_set, jsonfile)
#     await bot.send(ev,f"设置成功，当前设置如下：\n禁止抽签：{raw_set['disable']}\n初詣：{raw_set['chuyi']}")
    
    
    