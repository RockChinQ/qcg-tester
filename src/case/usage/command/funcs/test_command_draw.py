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


class TestCommandDraw:
    @pytest.mark.asyncio
    async def test_command_draw(self):
        qcg.ensure_qchatgpt(pwd="resource/")

        # 删除database.db
        await system.run_command_async(
            command="rm -rf database.db",
            cwd="resource/QChatGPT",
            timeout=2,
        )

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=2,
        )

        resp: list[str] = []

        resp_url: list[str] = []

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

            temp_url = ""

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    temp_str += message["text"]
                elif message["type"] == "Image":
                    temp_url = message["url"]

            msgId += 1

            await mock.skittles_app.send(
                mock._bots[0], {"code": 0, "msg": "success", "messageId": msgId}, '{}'.format(data["syncId"])
            )

            if temp_str:
                resp.append(temp_str)
            if temp_url:
                resp_url.append(temp_url)


        data = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {
                    "type": "Plain",
                    "text": "!draw Robot",
                },
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=20,
        )

        await asyncio.gather(mock.run())

        logging.info(
            "run done: time: %s", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        print(resp)

        assert len(resp_url) == 1