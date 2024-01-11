import os
import json
import asyncio
import logging
import time

import pytest

from skittles.platform import mirai
from skittles.entity import bot, connection

from src.util import qcg, system, config
from src.contrib.mock import mah


class TestCompletion:
    @pytest.mark.asyncio
    async def test_completion(self):
        qcg.ensure_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=3,
        )

        check_config = mah.MiraiAPIHTTPMock.default_check_config.copy()
        check_config['completion_api_params'] = """{
    "model": "gpt-3.5-turbo-instruct",
}"""

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
                {"type": "Plain", "text": "Only reply a 'Hello' to me."},
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=20,
            check_config=check_config,
        )
        
        await mock.run()

        assert resp.strip()
        assert "[bot]" not in resp.lower()
        assert "hello" in resp.lower()