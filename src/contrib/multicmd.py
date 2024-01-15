import time
import logging
import json
import datetime
import asyncio

from skittles.platform import mirai
from skittles.entity import bot, connection

from .mock import mah


class MultiMessageTester:

    _cases: list[tuple]

    _send_msg_id: int = 10000

    event_data_template = {}

    resp: list[str] = []

    source_msg_id: int = 0

    mock: mah.MiraiAPIHTTPMock = None

    def __init__(self, cases: list[tuple], wait_timeout: int = 15, coverage_file: str = None, exclude_msg_contains: list[str] = []):
        self._cases = cases

        self._send_msg_id = 10000
        self.event_data_template = {
            "type": "FriendMessage",
            "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
            "messageChain": [
                {"type": "Source", "id": 0, "time": 0},  # id, time changed each time
                {
                    "type": "Plain",
                    "text": "",  # text changed each time
                },
            ],
        }
        self.resp = []
        self.source_msg_id = 0
        self.mock = None

        async def handler(
            bot: bot.Bot, connection_type: connection.ConnectionType, data: str
        ) -> None:
            
            data = json.loads(data)

            logging.info(
                f"received data: {data} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            temp_str = ""

            for message in data["content"]["messageChain"]:
                if message["type"] == "Plain":
                    temp_str += message["text"]

            self._send_msg_id += 1

            await self.mock.skittles_app.send(
                self.mock._bots[0], {"code": 0, "msg": "success", "messageId": self._send_msg_id}, '{}'.format(data["syncId"])
            )

            if any([x in temp_str for x in exclude_msg_contains]):
                return
            self.resp.append(temp_str)

        self.mock = mah.MiraiAPIHTTPMock(
            action_handler=handler,
            converage_file=coverage_file,
            wait_timeout=wait_timeout,
        )


    async def run(self) -> list[str]:
        
        async def send_sequence():
            await asyncio.sleep(4)

            seq = 10000

            for case in self._cases:
                logging.info("send_sequence: %s", case)
                self.event_data_template["messageChain"][0]["id"] = seq
                self.event_data_template["messageChain"][0]["time"] = int(time.time())
                self.event_data_template["messageChain"][1]["text"] = case[0]
                seq += 1

                await self.mock.skittles_app.send(
                    self.mock._bots[0],
                    self.event_data_template,
                    "-1",
                )

                await asyncio.sleep(case[1])

        await asyncio.gather(self.mock.run(), send_sequence())

        return self.resp
