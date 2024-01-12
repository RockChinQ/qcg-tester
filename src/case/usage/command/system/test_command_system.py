import pytest
import logging

from src.contrib import multicmd
from src.util import qcg, system, config


class TestCommandSystem:
    @pytest.mark.asyncio
    async def test_command_system(self):
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

        # !cmd -> '当前所有命令' in resp
        # !cmd help -> '显示自定义的帮助信息' in resp
        # !help -> '此机器人通过调用大型语言模型生成回复' in resp
        # !usage -> '使用情况' in resp
        # !version -> '当前版本' in resp

        cmd_sleep_time = 1.5

        case_list = [
            (
                "!cmd",
                cmd_sleep_time,
                lambda x: "当前所有命令" in x,
            ),
            (
                "!cmd help",
                cmd_sleep_time,
                lambda x: "显示自定义的帮助信息" in x,
            ),
            (
                "!help",
                cmd_sleep_time,
                lambda x: "此机器人通过调用大型语言模型生成回复" in x,
            ),
            (
                "!usage",
                cmd_sleep_time,
                lambda x: "使用情况" in x,
            ),
            (
                "!version",
                cmd_sleep_time+3,
                lambda x: "当前版本" in x,
            ),
        ]

        multi_tester = multicmd.MultiMessageTester(
            cases=case_list,
            wait_timeout=sum([x[1] for x in case_list]) + 3,
            coverage_file=".coverage." + self.__class__.__name__,
        )

        resp = await multi_tester.run()

        index = 0

        for case in case_list:
            logging.info(f"Testing case: {case[0]} {resp[index]}")
            assert case[2](resp[index])
            index += 1
