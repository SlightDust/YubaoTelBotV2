import json
from aiotg import Bot, Chat

from yubao.util.logger import new_logger
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


def init(token, proxy=None, **kwargs):
    global _bot
    _bot = YubaoTelBot(api_token=token, proxy=proxy, **kwargs)
    logger.info("====================connected====================")
    return _bot

def get_bot() -> Bot:
    return _bot