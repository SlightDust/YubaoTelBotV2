import json
from aiotg import Chat

async def at_sender(chat:Chat):
    cid = chat.id
    uid = chat.message.get("from").get('id')
    uname = chat.message.get('from').get('username')
    ufstname = chat.message.get('from').get('first_name')
    # print(uid, uname, ufstname)
    if uname is not None:
        # 发送者设置了username，优先以@username的形式创建mention
        at = f"[{{'offset': 0, 'length': {1+len(uname)}, 'type':'mention', }}]"
        return f'@{uname}', None
        # await chat.send_text(text=f'@{uname}')
    else:
        # 发送者未设置username，创建text_mention
        at = [
            {'offset': 0, 
             'length': len(ufstname), 
             'type': 'text_mention', 
             'user':{'id': uid, 
                     'is_bot': False, 
                     'first_name': ufstname
                     }
            }]
        return f'{ufstname}', json.dumps(at, ensure_ascii=False)
        # await chat.send_text(text=f'{ufstname}', entities=json.dumps(at, ensure_ascii=False))

async def at_callbacker(cq):
    uid = cq.src.get("from").get('id')
    uname = cq.src.get('from').get('username')
    ufstname = cq.src.get('from').get('first_name')
    # print(uid, uname, ufstname)
    if uname is not None:
        # 发送者设置了username，优先以@username的形式创建mention
        at = f"[{{'offset': 0, 'length': {1+len(uname)}, 'type':'mention', }}]"
        return f'@{uname}', None
        # await chat.send_text(text=f'@{uname}')
    else:
        # 发送者未设置username，创建text_mention
        at = [
            {'offset': 0, 
             'length': len(ufstname), 
             'type': 'text_mention', 
             'user':{'id': uid, 
                     'is_bot': False, 
                     'first_name': ufstname
                     }
            }]
        return f'{ufstname}', json.dumps(at, ensure_ascii=False)
        # await chat.send_text(text=f'{ufstname}', entities=json.dumps(at, ensure_ascii=False))