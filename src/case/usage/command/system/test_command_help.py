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

        config.ensure_config(
            "admin_qq",
            "1010553892",
            cwd="resource/QChatGPT",
        )

        config.ensure_config(
            "msg_source_adapter",
            "'yirimirai'",
            cwd="resource/QChatGPT",
        )


        config.ensure_config(
            "mirai_http_api_config",
            """{
    "adapter": "WebSocketAdapter",
    "host": "localhost",
    "port": 8182,
    "verifyKey": "yirimirai",
    "qq": 12345678
}""",
            cwd="resource/QChatGPT",
        )

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            data = json.loads(data)

            resp = ""

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    resp += message["text"]

            assert '此机器人通过调用大型语言模型生成回复' in resp

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
            wait_timeout=3,
        )

        await mock.run()