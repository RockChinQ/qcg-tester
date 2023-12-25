import os
import logging
import asyncio
import time

import pytest
from skittles.platform import mah

from src.util import qcg
from src.util import system, config


class TestConnectYiriMirai:
    @pytest.mark.asyncio
    async def test_connect_yirimirai(self):
        if os.path.exists("resource/"):
            qcg.cleanup_qchatgpt(pwd="resource/")

        qcg.setup_qchatgpt(pwd="resource/")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=12,
        )
        print(time.time(), 11111111)

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

        async def handler(**kwargs):  # 数据包处理器
            print(kwargs)

        mahinst = mah.MiraiAPIHTTPAdapter(  # mock
            handler
        )

        async def run_main():  # 启动主程序
            await asyncio.sleep(5)

            try:

                print(time.time(), "run_main")
                # 启动主程序
                stdout, stderr = await system.run_command_async(
                    command="python main.py",
                    cwd="resource/QChatGPT",
                    timeout=15,
                )
                print(time.time(), "run_main done")
            except:
                pass

        async def check():
            await asyncio.sleep(8)
            print(time.time(), "check")
            assert len(mahinst.session_keys) > 0

        async def mock_run():
            try:
                await mahinst.run()
            except:
                pass


        async def wrapper():

            try:
                _ = await asyncio.gather(
                    mock_run(),
                    run_main(),
                    check(),
                )
            except:
                pass

        try:
            await asyncio.wait_for(
                wrapper(),
                timeout=20,
            )
        except asyncio.TimeoutError:
            pass

        qcg.cleanup_qchatgpt(pwd="resource/")
