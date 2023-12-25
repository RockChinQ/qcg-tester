import asyncio
import json
import time
import logging

logging.basicConfig(level=logging.DEBUG)

import websockets

from skittles.platform import mah

async def handler(**kwargs):
    print(kwargs)

mahadapter = mah.MiraiAPIHTTPAdapter(handler)


async def test():
    await asyncio.sleep(10)
    # print(mahadapter.get_session_keys())
    print(mahadapter.session_keys)
    print(len(mahadapter.session_keys))
    print(11111111111)

    # session_key = list(mahadapter.get_session_keys())[0]

    # data = {
    #         "type": "FriendMessage",
    #         "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
    #         "messageChain": [
    #             {"type": "Source", "id": 123456, "time": int(time.time())},
    #             {"type": "Plain", "text": "你好"},
    #         ],
    #     }

    # await mahadapter.send(session_key, data, '-1')


async def main():
    tasks = [mahadapter.run(), test()]

    await asyncio.gather(*tasks)


asyncio.run(main())
