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


class TestCommandSession:
    @pytest.mark.asyncio
    async def test_command_session(self):
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

        mock: mah.MiraiAPIHTTPMock = None

        msgId = 10000

        # 1. hello, my name is Rock, remember this and reply 'Hello, Rock!' please.
        # 2. !list -> hello in resp
        # 3. !prompt -> hello in resp
        # 4. !reset -> 会话已重置 in resp
        # 5. what's my name -> 'rock' not in resp
        # 6. my name is Soulter, remember this and reply 'Hello, Soulter!' please -> 'soulter' in resp
        # 7. !last -> 已切换到前一次的对话
        # 8. what's my name -> 'rock' in resp
        # 9. !last -> 已切换到前一次的对话
        # 10. what's my name -> 'soulter' in resp
        # 11. !last -> 已切换到前一次的对话
        # 12. !next -> 已切换到后一次的对话
        # 13. !resend -> 'soulter' in resp
        # 14. !list -> 'rock' in resp
        # 15. !del 1 -> 已删除历史会话
        # 16. !list -> 'rock' not in resp
        # 17. !delhst person_1010553892 -> 已删除会话
        # 18. !default -> '当前所有情景预设' in resp

        cmd_sleep_time = 1.5
        msg_sleep_time = 8

        case_list = [
            (
                "hello, my name is Rock, reply 'Hello, Rock!'",
                msg_sleep_time,
                lambda x: "hello" in x.lower(),
            ),
            (
                "!list",
                cmd_sleep_time,
                lambda x: "hello" in x.lower(),
            ),
            (
                "!prompt",
                cmd_sleep_time,
                lambda x: "hello" in x.lower(),
            ),
            (
                "!reset",
                cmd_sleep_time,
                lambda x: "会话已重置" in x,
            ),
            (
                "what's my name",
                msg_sleep_time,
                lambda x: "rock" not in x.lower(),
            ),
            (
                "my name is Soulter, reply 'Hello, Soulter!' please",
                msg_sleep_time,
                lambda x: "soulter" in x.lower(),
            ),
            (
                "!last",
                cmd_sleep_time,
                lambda x: "已切换到前一次的对话" in x,
            ),
            (
                "what's my name",
                msg_sleep_time,
                lambda x: "rock" in x.lower(),
            ),
            (
                "!last",
                cmd_sleep_time,
                lambda x: "已切换到前一次的对话" in x,
            ),
            (
                "what's my name",
                msg_sleep_time,
                lambda x: "soulter" in x.lower(),
            ),
            (
                "!last",
                cmd_sleep_time,
                lambda x: "已切换到前一次的对话" in x,
            ),
            (
                "!next",
                cmd_sleep_time,
                lambda x: "已切换到后一次的对话" in x,
            ),
            (
                "!resend",
                msg_sleep_time,
                lambda x: "soulter" in x.lower(),
            ),
            (
                "!list",
                cmd_sleep_time,
                lambda x: "rock" in x.lower(),
            ),
            (
                "!del 1",
                cmd_sleep_time,
                lambda x: "已删除历史会话" in x,
            ),
            (
                "!list",
                cmd_sleep_time,
                lambda x: "rock" not in x.lower(),
            ),
            (
                "!delhst person_1010553892",
                cmd_sleep_time,
                lambda x: "已删除会话" in x,
            ),
            (
                "!default",
                cmd_sleep_time,
                lambda x: "当前所有情景预设" in x,
            ),
            # (
            #     "according to the context, tell me what my name is",
            #     msg_sleep_time,
            #     lambda x: "soulter" in x.lower(),
            # ),
        ]

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

            resp.append(temp_str)

        data = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 123456, "time": int(time.time())},
                {
                    "type": "Plain",
                    "text": "!list",
                },
            ],
        }

        mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            first_data=data,
            converage_file=".coverage." + self.__class__.__name__,
            wait_timeout=75,
        )

        async def send_sequence():
            await asyncio.sleep(10)

            seq = 123457

            for case in case_list:
                logging.info("send_sequence: %s", case)
                await mock.skittles_app.send(
                    mock._bots[0],
                    {
                        "type": "FriendMessage",
                        "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                        "messageChain": [
                            {"type": "Source", "id": seq, "time": int(time.time())},
                            {
                                "type": "Plain",
                                "text": case[0],
                            },
                        ],
                    },
                    "-1",
                )

                seq += 1

                await asyncio.sleep(case[1])

            logging.info("send_sequence done")

        await asyncio.gather(mock.run(), send_sequence())

        logging.info(
            "run done: time: %s", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        print(resp)

        index = 1

        for case in case_list:
            assert case[2](resp[index])
            index += 1
