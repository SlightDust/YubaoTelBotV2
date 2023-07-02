# 系统库引用
import datetime
import random
import math
import calendar

# 三方库引用
from aiotg import Chat
from aiotg.bot import BotApiError
from PIL import Image, ImageDraw, ImageFont

# 自目录引用
import yubao
import yubao.util.aiorequest
from yubao import extendChat
from yubao.util.make_at import at_sender, at_callbacker
from yubao.util.sqlite import Sqlite 
from yubao.util.score import Score
from yubao.util.imageProcess import Image2BufferedReader
from yubao.util.logger import new_logger
bot = yubao.get_bot()
from yubao.config import Config
config = Config().read_config()

logger = new_logger("login_bonus")

dbfile = config['login_bonus_db']

with Sqlite(dbfile) as sqliter:
    if not sqliter.check_table_exists("login_detail"):
        sqliter.create_table("login_detail","id INTEGER PRIMARY KEY, first_name TEXT, user_id TEXT, username TEXT, chat_id TEXT, chat_title TEXT, chat_type TEXT, date DATE")
    if not sqliter.check_table_exists("login"):
        sqliter.create_table("login","id INTEGER PRIMARY KEY, user_id TEXT, total INTEGER, consecutive_days INTEGER, last_date DATE")

NUM_NAME = (
    '〇〇', '〇一', '〇二', '〇三', '〇四', '〇五', '〇六', '〇七', '〇八', '〇九',
    '一〇', '一一', '一二', '一三', '一四', '一五', '一六', '一七', '一八', '一九',
    '二〇', '二一', '二二', '二三', '二四', '二五', '二六', '二七', '二八', '二九',
    '三〇', '三一', '三二', '三三', '三四', '三五', '三六', '三七', '三八', '三九',
    '四〇', '四一', '四二', '四三', '四四', '四五', '四六', '四七', '四八', '四九',
    '五〇', '五一', '五二', '五三', '五四', '五五', '五六', '五七', '五八', '五九',
    '六〇', '六一', '六二', '六三', '六四', '六五', '六六', '六七', '六八', '六九',
    '七〇', '七一', '七二', '七三', '七四', '七五', '七六', '七七', '七八', '七九',
    '八〇', '八一', '八二', '八三', '八四', '八五', '八六', '八七', '八八', '八九',
    '九〇', '九一', '九二', '九三', '九四', '九五', '九六', '九七', '九八', '九九',
)

MONTH_NAME = ('睦月', '如月', '弥生', '卯月', '皐月', '水無月',
              '文月', '葉月', '長月', '神無月', '霜月', '師走')

def month_name(x: int) -> str:
    return MONTH_NAME[x - 1]

todo_list = [
    # '和明桥下五子棋',
    '来一把五子棋',
    # '看玄裳女装',
    '来一段niconiconi',
    '来点涩图',
    # '听玄翼和剑舞唱StartDash',
    '去B站看看帝域的投稿',
    '为域宝举牌',
    '去学日语',
    '来一发十连',
    '氪一单',
    '成为魔法少女',
    '搓一把日麻',
    # '给期刊投稿',
    '变成美少女',
    '给域宝telegram-bot仓库点个star',
    '去试试telegram版域宝'
]

def get_score_rank(total):
    # 属于是不会算数学了
    '''
    5,50,100,150,195
    '''
    if total >= 500:
        rank = 6
        start = 500
        end = rank * 100 + (rank + 1) ** 3
        while end < total:
            print(f"rank{rank},{start},{end}")
            rank += 1
            start = end
            end = rank * 100 + (rank + 1) ** 3

    else:
        if total < 5:
            rank = 1
            start = 0
            end = 5
        elif total < 55:
            rank = 2
            start = 5
            end = 55
        elif total < 100:
            rank = 3
            start = 55
            end = 155
        elif total < 305:
            rank = 4
            start = 155
            end = 305
        else:
            rank = 5
            start = 305
            end = 500

    return rank, math.floor(start), math.floor(end)

async def get_date_logined(uid: str, year, month) -> list:
    res = []
    sql = f"SELECT `date` FROM `login_detail` WHERE `user_id`='{uid}' AND `date`='{datetime.date.today}'"
    with Sqlite(dbfile) as sqliter:
        cursor = await sqliter.execute_sql(sql)
        data = cursor.fetchmany(31)
    for i in data:
        res.append(int(str(i[0]).split('-')[2]))
    return res

def year_name(year: int) -> str:
    return NUM_NAME[int(year / 100)] + NUM_NAME[year % 100]



@bot.command(r'^(域宝)?签到$')
async def login_bonus(chat:Chat, match):
    logger.info(f'收到来自{chat.sender} from {chat.type} chat {chat.id} 的 login_bonus 消息: {chat.message}')
    if 'private' in chat.type:
        chat.reply("请在群聊中使用该功能~")
        return
    signed, data = await already_signed(chat=chat)
    # id, first_name, user_id, username, chat_id, chat_tiale, chat_type, date
    old_total, old_cons, last_date = await init_user(chat)  # 在签到统计表中初始化
    if signed:
        # 已经签到过了
        chat.reply("主人您已经签到过了，请明天再来~")
        pass
    else:
        # 今天还没签过
        # 发送可可萝盖章
        today = datetime.date.today()
        yestoday = today - datetime.timedelta(days=1)  # 昨天的日期
        total_days = old_total + 1
        cons = old_cons+1 if last_date == str(yestoday) else 1
        ## 更新签到统计表
        sql = f"UPDATE login SET total={total_days}, consecutive_days={cons}, last_date='{today}' WHERE user_id={chat.get_uid()};"  
        ## 插入签到详情表
        group_title = chat.message.get('chat').get('title')
        sql1 = f"INSERT INTO login_detail('first_name', 'user_id', 'username', 'chat_id', 'chat_title', 'chat_type', 'date') VALUES('{chat.get_first_name()}', '{chat.get_uid()}', '{chat.get_username()}', {chat.id} ,'{group_title}', '{chat.type}', '{today}')"
        async with Sqlite(dbfile) as sqliter:
            await sqliter.execute_sql(sql)
            await sqliter.execute_sql(sql1)
        add = cons if cons <= 7 else 7
        score = await Score(chat).add_score(add)
        
        # 画图要素：uid, add, score(总分), total_days, cons, last_date, todo, chat(新增)
        todo = random.choice(todo_list)
        last_date = "0" if str(last_date)=="1970-01-01" else last_date
        image = await draw_pic_login(chat.get_uid(), add, score, total_days, cons, last_date, todo, chat)
        # image.show()
        photo = await Image2BufferedReader(image)
        await chat.reply_photo(photo=photo)
        pass

async def init_user(chat:Chat):
    chat.__class__ = extendChat
    sql = f"SELECT * FROM login WHERE user_id='{chat.get_uid()}'"
    async with Sqlite(dbfile) as sqliter:
        cursor = await sqliter.execute_sql(sql)
        data = cursor.fetchone()
        if data is None:
            sql1 = f"INSERT INTO login (user_id, total, consecutive_days, last_date) VALUES('{chat.get_uid()}',0,0,'1970-01-01')"
            await sqliter.execute_sql(sql1)
            return 0, 0,'1970-01-01'
        return data[2], data[3], data[4]


async def already_signed(chat:Chat):
    chat.__class__ = extendChat
    today = datetime.date.today()
    sql = f"SELECT * FROM login_detail WHERE user_id='{chat.get_uid()}' AND date='{today}'"
    # print(sql)
    async with Sqlite(dbfile) as sqliter:
        cursor = sqliter.conn.cursor()
        cursor.execute(sql)
        one = cursor.fetchone()
        if one is not None:
            return True, one  # 查询到不为空，说明今天签过
        return False, None  # 否则，未签过

background_img_path = './res/img/login_bonus/87126224.jpg'
img_sign_path = './res/img/login_bonus/kokkoro_stamp.png'
font_path = './res/font/hyxm.ttf'
font_path_fzmw = './res/font/FZMiaoWuK.TTF'
#  os.path.join(os.path.dirname(__file__), './res/font/FZMiaoWuK.TTF')


async def draw_pic_login(uid, add, score, total_days, cons, last_date, todo, chat:Chat):
    chat.__class__ = extendChat
    head_br = await bot.get_user_head(uid=uid)
    if head_br:
        head = Image.open(head_br)
        head = head.resize((100,100))
    else:
        head = Image.new("RGB",size=(100,100),color="white")
        draw = ImageDraw.Draw(head,"RGB")
        font = ImageFont.truetype("./res/font/sakura.ttf",36)
        word = "no\navatar"
        draw.text((5, 10),text=word,fill="#000000",font=font)
    # head.show()
    # 生成底图框架，定义draw和font
    width = 600
    height = 400
    img = Image.new("RGB", (width, height), (233, 233, 233))
    background_img = Image.open(background_img_path)
    background_img = background_img.resize((width, height))
    img.paste(background_img, (0, 0))
    img_bk = Image.new("RGBA", (width, height), (255, 255, 255, 230))
    a = img_bk.split()[3]
    img.paste(img_bk, (0, 0), mask=a)
    draw = ImageDraw.Draw(img)
    font1_small = ImageFont.truetype(font_path, 14)
    font1 = ImageFont.truetype(font_path, 18)
    font1_little_big = ImageFont.truetype(font_path, 20)
    font1_big = ImageFont.truetype(font_path, 24)
    font1_large = ImageFont.truetype(font_path, 38)
    font2 = ImageFont.truetype(font_path_fzmw, 22)
    
    # 贴title （320可用
    title = "欢  迎  回  来"
    width_title = font1_large.getsize(title)[0]
    draw.text(((320 - width_title) / 2, 10), title, fill=(220, 40, 0), font=font1_large)

    # 贴头像
    img.paste(head, (10, 150))

    # 获取年月
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    hour = datetime.datetime.now().hour

    # 查询当月签到过的日期
    logined = await get_date_logined(uid, year, month)
    logined.append(day)

    # 打开kkr印章
    img_sign = Image.open(img_sign_path)
    img_sign = img_sign.resize((32, 32))

    # 获取并绘制当月日历
    # 对当月签到过的日期标记
    # 对今天盖章
    monthRange = calendar.monthrange(year, month)
    day_one_is_nanyoubi = monthRange[0] + 1 + 1  # 当前月份的第一天是周几（1-7）
    days_in_current_month = monthRange[1]  # 当前月份共多少天
    width_calendar = 280
    img_calendar = Image.new("RGBA", (width_calendar, 280), (233, 233, 233, 0))
    draw_calendar = ImageDraw.Draw(img_calendar)
    _title = f"{year_name(year)}·{month_name(month)}"
    _title_size = font1_big.getsize(_title)
    draw_calendar.text(((width_calendar - _title_size[0]) / 2, 5), _title, fill=(0, 0, 0), font=font2)  # 打印签到表标题
    week_size = font1_big.getsize("日  一  二  三  四  五  六")
    # print(week_size)
    draw_calendar.text(((width_calendar - week_size[0]) / 2, 40), "日  一  二  三  四  五  六", fill=(0, 0, 0),
                       font=font1_big, )
    day_start = (width_calendar - week_size[0]) / 2
    day_width = week_size[0] / 7
    for i in range(day_one_is_nanyoubi, days_in_current_month + day_one_is_nanyoubi):
        # 我的天啊这是什么我已经看不懂了，为什么取余266，266是哪来的？？？
        x = int((day_start * (i / 7 + 1) + day_width * (i - 1)) % 266)
        y = 40 + 30 * math.ceil(i / 7) + 1
        # print(x, y)
        fill = (0, 0, 0)
        draw_calendar.text((x, y),
                           str(i - day_one_is_nanyoubi + 1),
                           fill=fill,
                           font=font1_little_big)
        if (i - day_one_is_nanyoubi + 1) in logined:
            # 做已签到标记
            a = img_sign.split()[3]  # 读取透明通道
            img_calendar.paste(img_sign, (x, y), mask=a)
            img_calendar.paste(img_sign, (x, y), mask=a)
            img_calendar.paste(img_sign, (x, y), mask=a)
            # draw_calendar.text((x, y + 5), "√", fill=(240, 0, 0), font=font1_little_big)
        draw_calendar.text((100,260), "*数据起始于2023-07-02", fill=(190, 190, 190), font=font1_small)

    # 日期贴到大图上
    a = img_calendar.split()[3]
    img.paste(img_calendar, (width - width_calendar, 0), mask=a)
    # 其他文字内容
    draw.text((10, 60), chat.get_first_name() or chat.get_username(), fill=(0, 0, 0), font=font1)
    today = f"{month:02d}/{day:02d}"
    draw.text((170, 90), today, fill=(0, 0, 0), font=font1_large)
    word = {0: "晚安", 1: "晚安", 2: "晚安", 3: "晚安", 4: "晚安", 5: "晚安", 6: "早安", 7: "早安", 8: "早安", 9: "上午好", 10: "上午好",
            11: "上午好", 12: "中午好", 13: "中午好", 14: "中午好", 15: "下午好", 16: "下午好", 17: "下午好", 18: "下午好", 19: "晚上好",
            20: "晚上好", 21: "晚上好", 22: "晚上好", 23: "晚安"}

    draw.text((10, 90), word[hour], fill=(0, 0, 0), font=font1_large)
    draw.text((115, 150), f"积分 ", fill=(0, 0, 0), font=font1_big)
    draw.text((115 + font1_big.getsize("积分 ")[0], 150), f"+ {add}", fill=(200, 0, 0), font=font1_big)
    draw.text((115, 190), f"总积分 ", fill=(0, 0, 0), font=font1_big)
    draw.text((115 + font1_big.getsize("总积分 ")[0], 190), f"{score}", fill=(200, 0, 0), font=font1_big)

    rank, start, end = get_score_rank(score)
    if score != "Error":
        draw.text((115, 230), f"积分等级：", fill=(0, 0, 0), font=font1_big)
        draw.text((115 + font1_big.getsize("积分等级：")[0] - 5, 230), f"rank {rank}", fill=(200, 0, 0), font=font1_big)

        draw.rectangle((10, 275, 320, 281), fill=(200, 200, 200))  # 总条
        percent = (score - start) / (end - start)  # 经验百分比
        draw.rectangle((10, 273, 10 + 310 * percent, 278), fill=(0, 200, 0))  # 当前经验
        draw.text((5, 280), f"{start}", fill=(0, 0, 0), font=font1_small)
        end_size = font1.getsize(str(end))[0]  # 长度
        draw.text((330 - end_size, 280), f"{end}", fill=(0, 0, 0), font=font1_small)

    draw.text((10, 300), f"您已累计签到{total_days}天，连续签到{cons}天啦", fill=(0, 0, 0), font=font1)
    draw.text((10, 330), f"上次签到时间是{last_date if last_date != '0' else '……主人这是您第一次使用域宝签到，请以后常来~'}", fill=(0, 0, 0), font=font1)
    draw.text((10, 360), f"主人今天要去{todo}吗？", fill=(0, 0, 0), font=font1)
    # show
    # img.show()
    # img_calendar.show()
    return img