import os
import json
import asyncio
import logging
import time

import pytest

from skittles.platform import mirai
from skittles.entity import bot, connection

from src.util import qcg, system, config


class TestGPT35Turbo:

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

        api_key = os.environ['OPENAI_API_KEY'] if 'OPENAI_API_KEY' in os.environ else "OPENAI_API_KEY"
        reverse_proxy = os.environ['OPENAI_REVERSE_PROXY'] if 'OPENAI_REVERSE_PROXY' in os.environ else "OPENAI_REVERSE_PROXY"

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

        resp = ''

        bot_account = [
            bot.Bot(
                account_id='12345678',
                nickname='Bot',
                connection_types=[connection.ConnectionType.FORWARD_WS]
            )
        ]

        app = mirai.MiraiAPIHTTPAdapter()

        @app.action_handler
        async def handler(bot: bot.Bot, connection_type: connection.ConnectionType, data: str) -> None:
            nonlocal resp

            data = json.loads(data)

            logging.info(f"Received message: {data}, {type(data)}")

            resp = ''

            for message in data['content']['messageChain']:
                if message['type'] == 'Plain':
                    resp += message['text']

        async def test():
            await asyncio.sleep(6)

            data = {
                "type": "FriendMessage",
                "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                "messageChain": [
                    {"type": "Source", "id": 123456, "time": int(time.time())},
                    {"type": "Plain", "text": "Only reply a 'Hello' to me."},
                ],
            }

            await app.emit_event(bots=bot_account, event=data)
            logging.info("Test message sent.")

            await asyncio.sleep(20)

            logging.info('Killing app.')
            await app.kill()

            assert 'hello' in resp.lower()

        async def launch():
            await asyncio.sleep(3)
            logging.info("Launching QChatGPT.")
            await system.run_command_async(
                command="python main.py",
                cwd="resource/QChatGPT",
                timeout=18,
            )
            logging.info("QChatGPT killed.")

        async def run():
            tasks = [app.run(bots=bot_account), launch(), test()]

            await asyncio.gather(*tasks)

        await run()