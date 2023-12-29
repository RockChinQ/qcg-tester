import json
import os
import typing
import asyncio

from skittles.platform import mirai
from skittles.entity import bot, connection

from src.util import qcg, system, config


class MiraiAPIHTTPMock:
    """使用 MAH 的测试用例的通用逻辑"""

    skittles_app: mirai.MiraiAPIHTTPAdapter

    default_check_config: dict[str, str]={
        "msg_source_adapter": "'yirimirai'",
        "admin_qq": "1010553892",
        "mirai_http_api_config": """{
    "adapter": "WebSocketAdapter",
    "host": "localhost",
    "port": 8182,
    "verifyKey": "yirimirai",
    "qq": 12345678
}""",
        "completion_api_params": """{
    "model": "gpt-3.5-turbo",
}""",
    }

    def __init__(
        self,
        action_handler: typing.Callable[
            [bot.Bot, connection.ConnectionType, str],
            typing.Coroutine[typing.Any, typing.Any, typing.Any],
        ],
        first_data: dict=None,
        converage_file: str=None,
        wait_timeout: int=30,
        bots: typing.List[bot.Bot]=[
            bot.Bot(
                account_id="12345678",
                nickname="Bot",
                connection_types=[connection.ConnectionType.FORWARD_WS],
            )
        ],
        check_config: dict[str, str]=default_check_config,
        set_openai_config: bool=True,
    ):
        """
        初始化控制器

        :param action_handler: 动作处理器
        :param first_data: 测试用例发起的第一个事件，如果为 None 则不发送
        :param converage_file: 覆盖率文件，如果为 None 则**不启动 QChatGPT**
        :param wait_timeout: 赋予 QChatGPT 的运行时间
        """
        self._action_handler = action_handler
        self._first_data = first_data
        self._converage_file = converage_file
        self._wait_timeout = wait_timeout
        self._bots = bots
        self._check_config = check_config
        self._set_openai_config = set_openai_config

    async def _run_skittles(self):
        """运行 skittles"""
        self.skittles_app = mirai.MiraiAPIHTTPAdapter()

        self.skittles_app.action_handler(self._action_handler)

        await self.skittles_app.run(bots=self._bots)

    async def _run_qchatgpt(self):
        """运行 QChatGPT"""
        await asyncio.sleep(1)

        if self._converage_file is not None:
            await system.run_python_with_coverage_async(
                command="main.py",
                cwd="resource/QChatGPT",
                coverage_file=self._converage_file,
                timeout=self._wait_timeout,
            )

    async def _send_first_data(self):
        """发送第一个事件"""
        await asyncio.sleep(5)

        if self._first_data is not None:
            await self.skittles_app.emit_event(bots=self._bots, event=self._first_data)

    async def _time_control(self):
        """时间控制"""
        await asyncio.sleep(self._wait_timeout+7)

        await self.skittles_app.kill()

    async def run(self):
        """以阻塞的方式运行控制器
        达到 wait_timeout 后，结束 QChatGPT 进程和 mock 实例
        """

        for key, value in self._check_config.items():
            config.ensure_config(
                key,
                value,
                cwd="resource/QChatGPT",
            )

        if self._set_openai_config:
            api_key = (
                os.environ["OPENAI_API_KEY"]
                if "OPENAI_API_KEY" in os.environ
                else "OPENAI_API_KEY"
            )
            reverse_proxy = (
                os.environ["OPENAI_REVERSE_PROXY"]
                if "OPENAI_REVERSE_PROXY" in os.environ
                else "OPENAI_REVERSE_PROXY"
            )

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

        tasks = [
            self._run_skittles(),
            self._run_qchatgpt(),
            self._send_first_data(),
            self._time_control(),
        ]

        await asyncio.gather(*tasks)
