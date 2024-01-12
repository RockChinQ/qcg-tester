import pytest
import logging

from src.contrib import multicmd
from src.util import qcg, system, config


class TestCommandCfg:
    @pytest.mark.asyncio
    async def test_command_cfg(self):
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

        # !cfg all -> 所有配置项 in resp
        # !cfg completion_api_params -> 'model' in resp
        # !cfg completion_api_params.model -> 'gpt-3.5-turbo' in resp
        # !cfg completion_api_params.model "gpt-3.5-turbo-16k"
        # !cfg completion_api_params.model -> 'gpt-3.5-turbo-16k' in resp
        # !cfg completion_api_params {'model':'gpt-3.5-turbo'} -> 修改成功
        # !cfg abcdefghijkl -> 未找到配置项
        # !cfg completion_api_params abcdefgh -> 不合法
        # !cfg completion_api_params.model 123 -> 类型不匹配

        cmd_sleep_time = 1.5

        case_list = [
            (
                "!cfg all",
                cmd_sleep_time,
                lambda x: "所有配置项" in x,
            ),
            (
                "!cfg completion_api_params",
                cmd_sleep_time,
                lambda x: "model" in x,
            ),
            (
                "!cfg completion_api_params.model",
                cmd_sleep_time,
                lambda x: "gpt-3.5-turbo" in x,
            ),
            (
                "!cfg completion_api_params.model \"gpt-3.5-turbo-16k\"",
                cmd_sleep_time,
                lambda x: "修改成功" in x,
            ),
            (
                "!cfg completion_api_params.model",
                cmd_sleep_time,
                lambda x: "gpt-3.5-turbo-16k" in x,
            ),
            (
                "!cfg completion_api_params {'model':'gpt-3.5-turbo'}",
                cmd_sleep_time,
                lambda x: "修改成功" in x,
            ),
            (
                "!cfg abcdefghijkl",
                cmd_sleep_time,
                lambda x: "未找到配置项" in x,
            ),
            (
                "!cfg completion_api_params abcdefgh",
                cmd_sleep_time,
                lambda x: "不合法" in x,
            ),
            (
                "!cfg completion_api_params.model 123",
                cmd_sleep_time,
                lambda x: "类型不匹配" in x,
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
