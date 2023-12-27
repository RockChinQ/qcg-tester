import os
import logging
import asyncio
import time

import pytest
from skittles.platform import mirai

from src.util import qcg
from src.util import system, config


class TestConnectYiriMirai:
    @pytest.mark.asyncio
    async def test_connect_yirimirai(self):
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

        pass