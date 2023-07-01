import json
from aiotg import Bot, Chat
import io

from yubao.util.logger import new_logger
from yubao.config import Config
config = Config().read_config()
import yubao.util.aiorequest
logger = new_logger("yubao")

_bot = None

class YubaoTelBot(Bot):

    def __init__(self, api_token, api_timeout=..., proxy=None, name=None, json_serialize=json.dumps, json_deserialize=json.loads, default_in_groups=False, connector=None):
        # initiation
        logger.info("====================initiating====================")
        super().__init__(api_token, api_timeout, proxy, name, json_serialize, json_deserialize, default_in_groups, connector)

    def send_photo(self, chat_id, photo, caption="",reply_to_message_id=None, **options):
        return self.api_call(
            "sendPhoto", chat_id=str(chat_id), photo=photo, caption=caption, reply_to_message_id=str(reply_to_message_id), **options
        )
    def copy_message(self, chat_id, from_chat_id, message_id, **options):
        return self.api_call(
            "copyMessage", chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, **options
        )
    async def get_user_head(self,uid):
        photos = await _bot.get_user_profile_photos(user_id=uid)
        # print(photos)
        try:
            photo_file_id = photos.get('result').get('photos')[0][0].get('file_id')
            photo = await _bot.get_file(file_id=photo_file_id)
            url = f"https://api.telegram.org/file/bot{config['token']}/{photo.get('file_path')}"
            # print(url)
            photo_file_coroutine = await yubao.util.aiorequest.get(url)
            photo_file = await photo_file_coroutine.content
            b_handle = io.BytesIO()
            b_handle.write(photo_file)
            b_handle.seek(0)
            b_handle.name = "temp.jpeg"
            b_br = io.BufferedReader(b_handle)
            return (b_br)
        except:
            return None

class extendChat(Chat):
    def __init__(self, bot, chat_id, chat_type="private", src_message=None):
        super(extendChat, self).__init__()
        super().__init__(bot, chat_id, chat_type, src_message)

    def get_uid(self):
        return str(self.message.get("from").get('id'))
    
    def get_username(self):
        return str(self.message.get("from").get('username'))
    
    def get_first_name(self):
        return self.message.get("from").get('first_name')
    

def init(token, proxy=None, **kwargs):
    global _bot
    _bot = YubaoTelBot(api_token=token, proxy=proxy, **kwargs)
    logger.info("====================connected====================")
    return _bot

def get_bot() -> Bot:
    return _bot