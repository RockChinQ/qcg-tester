import os
import json
import asyncio
import logging
import datetime
import time

import pytest
from skittles.platform import mirai
from skittles.entity import bot, connection

from src.util import qcg, system, config
from src.contrib.mock import mah


class TestPluginInstall:
    @pytest.mark.asyncio
    async def test_plugin_install(self):
        qcg.ensure_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=2,
        )

        resp: list[str] = []

        mock: mah.MiraiAPIHTTPMock = None

        msgId = 10000

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            nonlocal resp, msgId, mock

            data = json.loads(data)

            logging.info(
                f"received data: {data} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            temp_str = ""

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    temp_str += message["text"]

            msgId += 1

            await mock.skittles_app.send(
                mock._bots[0], {"code": 0, "msg": "success", "messageId": msgId}, '{}'.format(data["syncId"])
            )

            if "正在安装插件" in temp_str or "重载完成" in temp_str:
                return

            resp.append(temp_str)

        data = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {
                    "type": "Plain",
                    "text": "!plugin get https://github.com/RockChinQ/WebwlkrPlugin",
                },
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=40,
        )

        async def send_sequence():
            await asyncio.sleep(20)
            await mock.skittles_app.send(
                mock._bots[0],
                {
                    "type": "FriendMessage",
                    "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                    "messageChain": [
                        {"type": "Source", "id": 123456, "time": int(time.time())},
                        {
                            "type": "Plain",
                            "text": "!reload",
                        },
                    ],
                },
                "-1",
            )
            await asyncio.sleep(15)
            logging.info(
                "send first data after reload: time: %s",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            await mock.skittles_app.send(
                mock._bots[0],
                {
                    "type": "FriendMessage",
                    "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                    "messageChain": [
                        {"type": "Source", "id": 123456, "time": int(time.time())},
                        {
                            "type": "Plain",
                            "text": "!plugin",
                        },
                    ],
                },
                "-1",
            )
            await asyncio.sleep(2)
            await mock.skittles_app.send(
                mock._bots[0],
                {
                    "type": "FriendMessage",
                    "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                    "messageChain": [
                        {"type": "Source", "id": 123456, "time": int(time.time())},
                        {
                            "type": "Plain",
                            "text": "!plugin del Webwlkr",
                        },
                    ],
                },
                "-1",
            )
            logging.info("send_sequence done")

        await asyncio.gather(mock.run(), send_sequence())

        logging.info(
            "run done: time: %s", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # 删除 resource/QChatGPT/plugins/WebwlkrPlugin
        system.run_command(
            command="rm -rf resource/QChatGPT/plugins/WebwlkrPlugin",
            timeout=2,
        )

        print(resp)

        assert "插件安装成功" in resp[0]
        assert "Webwlkr" in resp[1]
        assert "已删除插件" in resp[2]
