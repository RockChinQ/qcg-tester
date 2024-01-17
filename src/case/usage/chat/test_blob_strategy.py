import pytest
import logging
import datetime
import json
import os

from skittles.entity import bot, connection

from src.contrib import multicmd
from src.util import qcg, system, config
from src.contrib.mock import mah


class TestBlobStrategy:
    @pytest.mark.asyncio
    async def test_blob_strategy(self):        
        qcg.ensure_qchatgpt(pwd="resource/")

        await system.run_command_async(
            command="rm -rf database.db",
            cwd="resource/QChatGPT",
            timeout=2
        )

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=2
        )

        msg_sleep_time = 8
        cmd_sleep_time = 3

        case_list = [
            (
                "Only reply a 'Hello' to me.",
                msg_sleep_time,
                lambda x: 'hello' in x.lower(),
            ),
            # (
            #     "!~blob_message_strategy \"image\"",
            #     cmd_sleep_time,
            #     lambda x: True,
            # ),

        ]
    
        config_dict = mah.MiraiAPIHTTPMock.default_check_config

        config_dict['blob_message_threshold'] = "1"
        config_dict['blob_message_strategy'] = '"forward"'
        config_dict['font_path'] = '"HiraginoSansGB.ttc"'

        # 把 assets/HiraginoSansGB.ttc 复制到 resource/QChatGPT/ 下
        system.run_command(
            command="cp assets/HiraginoSansGB.ttc resource/QChatGPT/",
            timeout=2
        )

        multi_tester: multicmd.MultiMessageTester = None

        img_received = {}

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            data = json.loads(data)

            logging.info(
                f"received data: {data} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            temp_str = ""

            for message in data["content"]["messageChain"]:
                if message["type"] == "Forward":
                    for msg_node in message['nodeList']:
                        for msg in msg_node['messageChain']:
                            if msg['type'] == "Plain":
                                temp_str += msg["text"]
                elif message['type'] == "Image":
                    temp_str += "image"
                    img_received = message

            multi_tester._send_msg_id += 1

            await multi_tester.mock.skittles_app.send(
                multi_tester.mock._bots[0],
                {"code": 0, "msg": "success", "messageId": multi_tester._send_msg_id},
                "{}".format(data["syncId"]),
            )

            multi_tester.resp.append(temp_str)

        multi_tester = multicmd.MultiMessageTester(
            cases=case_list,
            wait_timeout=sum([x[1] for x in case_list]),
            coverage_file=".coverage." + self.__class__.__name__,
            handler=handler
        )

        resp = await multi_tester.run()

        index = 0

        print(resp)

        for case in case_list:
            logging.info(f"Testing case: {case[0]} {resp[index]}")
            assert case[2](resp[index])
            index += 1

