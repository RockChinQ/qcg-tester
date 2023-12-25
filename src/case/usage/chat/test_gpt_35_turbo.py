import os
import json
import asyncio
import time

import pytest

from skittles.platform import mah

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

        config.set_config(
            "msg_source_adapter",
            "'yirimirai'",
            cwd="resource/QChatGPT",
        )

        config.set_config(
            "admin_qq",
            "123456789",
            cwd="resource/QChatGPT",
        )

        config.set_config(
            "mirai_http_api_config",
            """{
    "adapter": "WebSocketAdapter",
    "host": "localhost",
    "port": 8182,
    "verifyKey": "yirimirai",
    "qq": 1234567890
}""",
            cwd="resource/QChatGPT",
        )

        config.set_config(
            "completion_api_params",
            """{
    "model": "gpt-3.5-turbo",
}""",
            cwd="resource/QChatGPT",
        )

        api_key = os.environ['OPENAI_API_KEY'] if 'OPENAI_API_KEY' in os.environ else "OPENAI_API_KEY"
        reverse_proxy = os.environ['OPENAI_REVERSE_PROXY'] if 'OPENAI_REVERSE_PROXY' in os.environ else "OPENAI_REVERSE_PROXY"

        config.set_config(
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

        async def handler(*args, **kwargs):
            payload = json.loads(args[1]['body'])

            print(payload)

            plain_text_message = ''

            for msg in payload['content']['messageChain']:
                if msg['type'] == 'Plain':
                    plain_text_message += msg['text']

            nonlocal resp
            resp = plain_text_message

        mahinst = mah.MiraiAPIHTTPAdapter(
            handler
        )

        async def run_main():
            await asyncio.sleep(5)

            try:

                print(time.time(), "run_main")
                # 启动主程序
                stdout, stderr = await system.run_command_async(
                    command="python main.py",
                    cwd="resource/QChatGPT",
                    timeout=30,
                )
                print(time.time(), "run_main done")
            except:
                pass
        
        async def test():
            await asyncio.sleep(10)
            # print(mahadapter.get_session_keys())
            # print(mahadapter.session_keys)

            session_key = list(mahinst.get_session_keys())[0]

            data = {
                    "type": "FriendMessage",
                    "sender": {"id": 1010553892, "nickname": "Rock", "remark": ""},
                    "messageChain": [
                        {"type": "Source", "id": 123456, "time": int(time.time())},
                        {"type": "Plain", "text": "Please reply 'Hello'"},
                    ],
                }

            await mahinst.send(session_key, data, '-1')

        async def wrapper():
            try:
                _ = await asyncio.gather(
                    mahinst.run(),
                    run_main(),
                    test(),
                    return_exceptions=True,
                )
            except:
                pass

        try:
            await asyncio.wait_for(
                wrapper(),
                timeout=40,
            )
        except asyncio.TimeoutError:
            pass

        assert 'hello' in resp.lower()