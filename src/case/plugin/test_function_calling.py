import json
import asyncio
import logging
import time
import quart

import pytest

from skittles.platform import mirai
from skittles.entity import bot, connection

from src.util import qcg, system, config
from src.contrib.mock import mah


class TestFunctionCalling:

    @pytest.mark.asyncio
    async def test_function_calling(self):
        qcg.ensure_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=3,
        )

        # clone 插件
        system.run_command(
            command="git clone https://github.com/RockChinQ/WebwlkrPlugin",
            cwd="resource/QChatGPT/plugins",
            timeout=10,
        )

        # 安装依赖
        system.run_command(
            command="pip install -r requirements.txt",
            cwd="resource/QChatGPT/plugins/WebwlkrPlugin",
            timeout=10,
        )

        resp = ""

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            nonlocal resp

            data = json.loads(data)

            logging.info(f"Received message: {data}, {type(data)}")

            resp = ""

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    resp += message["text"]

        data = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {"type": "Plain", "text": "Access https://gist.githubusercontent.com/RockChinQ/23b586b3233aea2b23639dffce14c357/raw/e96f4bf83eeb529f75918222019a0a9345e46b20/gistfile1.txt"},
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=40,
        )
        
        await mock.run()

        # 删除插件
        await system.run_command_async(
            command="rm -rf WebwlkrPlugin",
            cwd="resource/QChatGPT/plugins",
            timeout=10,
        )

        assert "test" in resp.lower()