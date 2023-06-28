

import yaml
import re
import os
import math
import base64
import uuid
from os.path import dirname, join, exists

import ahocorasick
import aiofiles

import yubao.util.aiorequest as aiorequests
from . import translate


curpath = dirname(__file__) #当前路径
config_path = join(curpath,"config.yaml")
temp_image_path= join(curpath,'TempImage')  # 保存临时图片路径
if not exists(temp_image_path):
    os.mkdir(temp_image_path) #创建临时img保存目录


with open(config_path,encoding="utf-8") as f: #初始化配置文件
    config = yaml.safe_load(f)#读取配置文件

actree = ahocorasick.Automaton()#初始化AC自动机
for index, word in enumerate(config['wordlist']):
    actree.add_word(word, (index, word))
actree.make_automaton() #初始化完成，一般来说重启才能重载屏蔽词

async def guolv(sent):#过滤屏蔽词
    sent_cp = sent.lower() #转为小写
    tags_guolv = ""
    for i in actree.iter(sent):
        sent_cp = sent_cp.replace(i[1][1], "")
        tags_guolv = f"{tags_guolv} {str(i[1][1])} "
    return sent_cp,tags_guolv


async def pic_resize(width,height):
    c = width/height
    n = config["pic_max"] #最大像素
    if width*height > n:
        height = math.ceil(math.sqrt(n/c))
        width = math.ceil(c*height)
    width = math.ceil(width/64)*64
    height = math.ceil(height/64)*64 #等比缩放为64的倍数
    return width,height

async def pic_save_temp(imagedata):
    pid = str(uuid.uuid4())
    async with aiofiles.open(f"{temp_image_path}/{pid}.png", 'wb') as f:
        await f.write(imagedata)
    return pid


async def process_tags(gid,uid,tags,add_db=config['add_db'],trans=config['trans'],limit_word=config['limit_word'],arrange_tags=config['arrange_tags']):
    error_msg ="" #报错信息
    tags_guolv="" #过滤词信息
    #初始化
    try:
        tags = f"tags={tags.strip().lower()}" #去除首尾空格换行#转小写#头部加上tags= #转小写方便处理
        taglist = re.split('&',tags) #分割
        id = ["tags=","ntags=","seed=","scale=","shape=","strength=","r18=","steps=","sampler=","restore_faces=","tiling=","bigger=","w=","h="]
        tag_dict = {i: ("" if not [idx for idx in taglist if idx.startswith(i)] else [idx for idx in taglist if idx.startswith(i)][-1]).replace(i, '', 1)  for i in id }#取出tags+ntags+seed+scale+shape,每种只取列表最后一个,并删掉id
    except Exception as e:
        error_msg = f"tags初始化失败{e}"
        return tags,error_msg,tags_guolv
    #翻译tags
    if trans:
        try:
            if tag_dict["tags="] and tag_dict["ntags="]:
                tags2trans = f'{tag_dict["tags="]}&{tag_dict["ntags="]}' # &作为分隔符,为了整个拿去翻译
                tags2trans = await translate.tag_trans(tags2trans) #翻译
                taglist1 = re.split('&',tags2trans)
                tag_dict["tags="] = taglist1[0]
                tag_dict["ntags="] = taglist1[1]
            elif tag_dict["tags="]:
                tag_dict["tags="] = await translate.tag_trans(tag_dict["tags="])#翻译
        except Exception as e:
            error_msg += "翻译失败"

    #过滤tags,只过滤正面tags
    if limit_word:
        try:
            tag_dict["tags="],tags_guolv = await guolv(tag_dict["tags="].strip().lower())#过滤,转小写防止翻译出来大写
        except Exception as e:
            error_msg += "过滤失败"

    #整理tags
    if arrange_tags:
        try:
            #整理tags,去除空元素,去除逗号影响
            id2tidy = ["tags=","ntags="]
            for i in id2tidy:
                tidylist = re.split(',|，',tag_dict[i])
                while "" in tidylist:
                    tidylist.remove("")
                tag_dict[i] = ",".join(tidylist)
        except Exception as e:
            error_msg += f"整理失败{e}"

    #规范tags
    if not tag_dict["tags="]:
        tag_dict["tags="] = config['tags_moren']#默认正面tags
    if not tag_dict["ntags="]:
        tag_dict["ntags="] = config['ntags_moren']#默认负面tags
    if config["ntags_safe"]:
        tag_dict["ntags="] = (f"{config['ntags_safe']},{tag_dict['ntags=']}")#默认安全负面tags
    if tag_dict["shape="] and tag_dict["shape="] in ["portrait","landscape","square"]:
        tag_dict["shape="] = tag_dict["shape="].capitalize()
    else:
        tag_dict["shape="] = config['txt2img_shape_moren']#默认形状
    if not tag_dict["r18="]:
        tag_dict["r18="] = config['r18_moren']#默认r18参数
    if not tag_dict["restore_faces="] and tag_dict["restore_faces="] !=  "True":
        tag_dict["restore_faces="] = False#默认restore_faces
    if not tag_dict["tiling="] and tag_dict["tiling="] !=  "True":
        tag_dict["tiling="] = False#默认tiling
    tag_dict["bigger="] = False if not tag_dict["bigger="] else True#默认bigger
    # #上传XP数据库
    # if add_db:
    #     try:
    #         #上传XP数据库,只上传正面tags
    #         tags2XP = tag_dict["tags="]
    #         taglist3 = re.split(',',tags2XP)
    #         for tag in taglist3:
    #             db.add_xp_num(gid,uid,tag)
    #     except Exception as e:
    #         error_msg += "上传失败"
    return tag_dict,error_msg,tags_guolv



async def get_imgdata_sd(tagdict:dict,way=1,shape="Portrait",b_io=None,size = None):
    error_msg =""  #报错信息
    result_msg = ""
    if not tagdict["seed="]:
        tagdict["seed="] = -1
    if not way:
        shape = tagdict["shape="]
        if shape == "Portrait":
            width,height = 512,768
        elif shape == "Landscape":
            width,height = 768,512
        elif shape == "Square":
            width,height = 640,640
        if tagdict["bigger="]:
            width,height = width+128,height+128
        if tagdict["w="] and tagdict["w="].isdigit():
            width = int(tagdict["w="])
        if tagdict["h="] and tagdict["h="].isdigit():
            height = int(tagdict["h="])
        width,height = await pic_resize(width,height)#修正生成图的长宽为SD要求的64的倍数
        if not tagdict["steps="] or not tagdict["steps="].isdigit():
            tagdict["steps="] = config["txt2img_steps_moren"] #默认steps
        else:
            tagdict["steps="] = config["txt2img_steps_moren"]  if int(tagdict["steps="])>config["txt2img_steps_max"]  else tagdict["steps="]#超过最大步数
        if not tagdict["sampler="]:
            tagdict["sampler="] = config["txt2img_sampler_moren"]#默认sampler
        if not tagdict["scale="]:
            tagdict["scale="] = config['txt2img_scale_moren']#默认scale
        url = f"{config['sd_api_ip']}/sdapi/v1/txt2img"
        json_data = {
          "enable_hr": False,
          "prompt": tagdict["tags="],
          "seed": tagdict["seed="],
          "steps": tagdict["steps="],
          "cfg_scale": tagdict["scale="],
          "width": width,
          "height": height,
          "最大像素restore_faces": tagdict["restore_faces="],
          "tiling": tagdict["tiling="],
          "negative_prompt": tagdict["ntags="],
          "sampler_index": tagdict["sampler="]
        }

    if way :
        url = f"{config['sd_api_ip']}/sdapi/v1/img2img"
        data = ["data:image/jpeg;base64," + base64.b64encode(b_io.getvalue()).decode()]
        width,height = size
        if tagdict["bigger="]:
            width,height = width*2,height*2
        width,height = await pic_resize(width,height)#修正生成图的长宽为SD要求的64的倍数
        if not tagdict["strength="]:
            tagdict["strength="] = config['img2img_strength_moren']#默认噪声
        if not tagdict["steps="] or not tagdict["steps="].isdigit():
            tagdict["steps="] = config["img2img_steps_moren"] #默认steps
        else:
            tagdict["steps="] = config["img2img_steps_moren"]  if int(tagdict["steps="])>config["img2img_steps_max"]  else tagdict["steps="]#超过最大步数
        if not tagdict["sampler="]:
            tagdict["sampler="] = config["img2img_sampler_moren"]#默认sampler
        if not tagdict["scale="]:
            tagdict["scale="] = config['img2img_scale_moren']#默认scale
        json_data = {
            "init_images": data,
            "resize_mode": config["resize_mode"],
            "denoising_strength": tagdict["strength="],
            "prompt": tagdict["tags="],
            "seed": tagdict["seed="],
            "steps": tagdict["steps="],
            "cfg_scale": tagdict["scale="],
            "width": width,
            "height": height,
            "restore_faces": tagdict["restore_faces="],
            "tiling": tagdict["tiling="],
            "negative_prompt": tagdict["ntags="],
            "sampler_index": tagdict["sampler="]
        }
    try:
        response = await aiorequests.post(url,json=json_data,headers = {"Content-Type": "application/json"}, timeout=(6,360))
    except Exception as e:
        error_msg = f"API响应超时，请稍后再试{str(e).replace('192.168.2.5','*.*.*.*').replace('50010','*')}"
        return result_msg,error_msg    
    imgdata = await response.json()#报错反馈,待完成
    try:
        imgdata = imgdata["images"][0]
    except Exception as e:
        error_msg = f"响应为空，可能是SD API断开连接{e}"
        return result_msg,error_msg
    try :
        pid = await pic_save_temp(base64.b64decode(imgdata))
    except Exception as e:
        print(f"!!!保存失败{e}")
    try:
        imgmes = 'base64://' + imgdata
    except Exception as e:
        error_msg = f"处理图像失败{e}"
        return result_msg,error_msg
    result_msg = f"{temp_image_path}/{pid}.png"
    return result_msg,error_msg