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

    async def _run_skittles(self):
        """运行 skittles"""
        self.skittles_app = mirai.MiraiAPIHTTPAdapter()

        self.skittles_app.action_handler(self._action_handler)

        await self.skittles_app.run(bots=self._bots)

    async def _run_qchatgpt(self):
        """运行 QChatGPT"""
        await asyncio.sleep(2)

        if self._converage_file is not None:
            await system.run_python_with_coverage_async(
                command="main.py",
                cwd="resource/QChatGPT",
                coverage_file=self._converage_file,
                timeout=self._wait_timeout,
            )

    async def _send_first_data(self):
        """发送第一个事件"""
        await asyncio.sleep(4)

        if self._first_data is not None:
            await self.skittles_app.emit_event(bots=self._bots, event=self._first_data)

    async def _time_control(self):
        """时间控制"""
        await asyncio.sleep(self._wait_timeout+4)

        await self.skittles_app.kill()

    async def run(self):
        """以阻塞的方式运行控制器
        达到 wait_timeout 后，结束 QChatGPT 进程和 mock 实例
        """

        tasks = [
            self._run_skittles(),
            self._run_qchatgpt(),
            self._send_first_data(),
            self._time_control(),
        ]

        await asyncio.gather(*tasks)
