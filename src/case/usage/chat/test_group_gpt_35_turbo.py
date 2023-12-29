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


class TestGroupGPT35Turbo:
    @pytest.mark.asyncio
    async def test_gpt_35_turbo(self):
        qcg.ensure_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=3,
        )

        config.ensure_config(
            "msg_source_adapter",
            "'yirimirai'",
            cwd="resource/QChatGPT",
        )

        config.ensure_config(
            "admin_qq",
            "1010553892",
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

        config.ensure_config(
            "completion_api_params",
            """{
    "model": "gpt-3.5-turbo",
}""",
            cwd="resource/QChatGPT",
        )

        api_key = (
            os.environ["OPENAI_API_KEY"]
            if "OPENAI_API_KEY" in os.environ
            else "OPENAI_API_KEY"
        )
        reverse_proxy = (
            os.environ["OPENAI_REVERSE_PROXY"]
            if "OPENAI_REVERSE_PROXY" in os.environ
            else "OPENAI_REVERSE_PROXY"
        )

        config.ensure_config(
            "openai_config",
            f"""{{
    "api_key": {{
        "default": "{api_key}"
    }},
    "reverse_proxy": "{reverse_proxy}"
}}""",
            cwd="resource/QChatGPT",
        )

        resp = ""

        mock: mah.MiraiAPIHTTPMock = None

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            nonlocal resp

            data = json.loads(data)

            logging.info(f"Received message: {data}, {type(data)}")

            if data["command"] == "memberInfo":
                await mock.skittles_app.send(
                    bot=mock._bots[0],
                    data={
                        "id": 12345678,
                        "memberName": "Bot",
                        "specialTitle": "群头衔",
                        "permission": "MEMBER",
                        "joinTimestamp": 12345678,
                        "lastSpeakTimestamp": 8765432,
                        "muteTimeRemaining": 0,
                        "active": {
                            "rank": 6,
                            "point": 100,
                            "honors": ["群聊之火"],
                            "temperature": 100,
                        },
                        "group": {
                            "id": 12345,
                            "name": "Test Group",
                            "permission": "MEMBER",
                        },
                    },
                    sync_id=data["syncId"],
                )
            else:
                resp = ""

                for message in data["content"]["messageChain"]:
                    if message["type"] == "Plain":
                        resp += message["text"]

        data = {
            "type": "GroupMessage",
            "sender": {
                "id": 1010553892,
                "memberName": "Rock",
                "specialTitle": "",
                "permission": "OWNER",
                "joinTimestamp": 0,
                "lastSpeakTimestamp": 0,
                "muteTimeRemaining": 0,
                "group": {
                    "id": 123456,
                    "name": "Test Group",
                    "permission": "MEMBER",
                },
            },
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {"type": "Plain", "text": "aiOnly reply a 'Hello' to me."},
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=16,
        )

        await mock.run()

        assert "hello" in resp.lower()