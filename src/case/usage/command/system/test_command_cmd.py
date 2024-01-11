import os
import time
import json
import asyncio

import pytest
from skittles.entity import bot, connection

from src.contrib.mock import mah
from src.util import qcg, system, config

class TestCommandCmd:
    @pytest.mark.asyncio
    async def test_command_cmd(self):

        qcg.ensure_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=3,
        )

        resp = []
        msgId = 10000

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            nonlocal resp, msgId, mock

            data = json.loads(data)

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    resp.append(message["text"])
            
            await mock.skittles_app.send(
                mock._bots[0], {"code": 0, "msg": "success", "messageId": msgId}, '{}'.format(data["syncId"])
            )

        data = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {"type": "Plain", "text": "!cmd"},
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=15,
        )

        async def send_sequence():
            await asyncio.sleep(8)

            await mock.skittles_app.send(
                mock._bots[0],
                {
                    "type": "FriendMessage",
                    "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                    "messageChain": [
                        {"type": "Source", "id": 123456, "time": int(time.time())},
                        {
                            "type": "Plain",
                            "text": "!cmd help",
                        },
                    ],
                },
                "-1",
            )

        await asyncio.gather(mock.run(), send_sequence())

        print(resp)

        assert '当前所有指令' in resp[0]
        assert '显示自定义的帮助信息' in resp[1]