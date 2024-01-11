import os
import time
import json

import pytest
from skittles.entity import bot, connection

from src.contrib.mock import mah
from src.util import qcg, system, config

class TestCommandHelp:
    @pytest.mark.asyncio
    async def test_command_help(self):

        qcg.ensure_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=3,
        )

        resp = ""

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            nonlocal resp

            data = json.loads(data)

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    resp += message["text"]

        data = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {"type": "Plain", "text": "!help"},
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=5,
        )

        await mock.run()

        assert '此机器人通过调用大型语言模型生成回复' in resp