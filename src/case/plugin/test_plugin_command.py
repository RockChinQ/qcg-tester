import pytest
import logging

from src.contrib import multicmd
from src.util import qcg, system, config


class TestPluginCommand:
    @pytest.mark.asyncio
    async def test_plugin_command(self):
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

        cmd_sleep_time = 1.5

        case_list = [
            (
                "!plugin get https://github.com/RockChinQ/WebwlkrPlugin",
                cmd_sleep_time+8,
                lambda x: "安装成功" in x,
            ),
            (
                "!reload",
                cmd_sleep_time+3,
                lambda x: "重载完成" in x,
            ),
            (
                "!plugin",
                cmd_sleep_time,
                lambda x: "Webwlkr" in x,
            ),
            (
                "!plugin off Webwlkr",
                cmd_sleep_time,
                lambda x: "已禁用" in x,
            ),
            (
                "!plugin",
                cmd_sleep_time,
                lambda x: "已禁用" in x,
            ),
            (
                "!plugin on Webwlkr",
                cmd_sleep_time,
                lambda x: "已启用" in x,
            ),
            (
                "!plugin",
                cmd_sleep_time,
                lambda x: "已禁用" not in x,
            ),
            (
                "!plugin on abcdefg",
                cmd_sleep_time,
                lambda x: "未找到插件" in x,
            ),
            (
                "!plugin update Webwlkr",
                cmd_sleep_time + 3,
                lambda x: "已更新" in x,
            ),
            (
                "!plugin del Webwlkr",
                cmd_sleep_time,
                lambda x: "已删除" in x,
            ),
        ]

        multi_tester = multicmd.MultiMessageTester(
            cases=case_list,
            wait_timeout=sum([x[1] for x in case_list]) + 3,
            coverage_file=".coverage." + self.__class__.__name__,
            exclude_msg_contains=[
                "正在安装插件",
                "正在更新插件"
            ]
        )

        resp = await multi_tester.run()

        index = 0

        for case in case_list:
            logging.info(f"Testing case: {case[0]} {resp[index]}")
            assert case[2](resp[index])
            index += 1
