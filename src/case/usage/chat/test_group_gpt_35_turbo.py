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

        config.set_config(
            "response_rules",
            """{
    "default": {
        "at": True,  # 是否响应at机器人的消息
        "prefix": ["/ai", "!ai", "！ai", "ai"],
        "regexp": ["bot.*"],  # "为什么.*", "怎么?样.*", "怎么.*", "如何.*", "[Hh]ow to.*", "[Ww]hy not.*", "[Ww]hat is.*", ".*怎么办", ".*咋办"
        "random_rate": 0.0,  # 随机响应概率，0.0-1.0，0.0为不随机响应，1.0为响应所有消息, 仅在前几项判断不通过时生效
    },
}""",
            "resource/QChatGPT",
        )

        resp: list[str] = []

        mock: mah.MiraiAPIHTTPMock = None

        send_msg_id = 10000

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            nonlocal resp, send_msg_id

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
                temp_str = ""

                for message in data["content"]["messageChain"]:
                    if message["type"] == "Plain":
                        temp_str += message["text"]


                await mock.skittles_app.send(
                    mock._bots[0], {"code": 0, "msg": "success", "messageId": send_msg_id}, '{}'.format(data["syncId"])
                )

                send_msg_id += 1
                
                resp.append(temp_str)

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
            wait_timeout=25,
        )

        async def send_sequence():
            await asyncio.sleep(10)

            data["messageChain"] = [
                {"type": "Source", "id": 123457, "time": int(time.time())},
                {"type": "Plain", "text": "bot, Only reply a 'Hello' to me."},
            ]
            await mock.skittles_app.send(
                mock._bots[0],
                data,
                "-1"
            )
            await asyncio.sleep(8)

            data["messageChain"] = [
                {"type": "Source", "id": 123458, "time": int(time.time())},
                {"type": "At", "target": 12345678, "display": ""},
                {"type": "Plain", "text": "Only reply a 'Hello' to me."},
            ]
            await mock.skittles_app.send(
                mock._bots[0],
                data,
                "-1"
            )
            await asyncio.sleep(8)


        await asyncio.gather(mock.run(), send_sequence())

        print(resp)

        assert "hello" in resp[0].lower()
        assert "hello" in resp[1].lower()
        assert "hello" in resp[2].lower()