import os

import pytest

from src.util import qcg
from src.util import system

file_to_check = [
    "config.py",
    "banlist.py",
    "tips.py",
    "sensitive.json",
    "cmdpriv.json"
]


class TestFileGeneration:
    @pytest.mark.asyncio
    async def test_file_generation(self):
        """ 测试配置文件正常生成 """
        if os.path.exists("resource/"):
            qcg.cleanup_qchatgpt(pwd="resource/")

        qcg.setup_qchatgpt(pwd="resource/")

        for file in file_to_check:
            assert not os.path.exists(f"resource/QChatGPT/{file}")

        await system.run_python_with_coverage_async(
            command="main.py",
            cwd="resource/QChatGPT",
            coverage_file=".coverage."+self.__class__.__name__,
            timeout=20,
        )

        for file in file_to_check:
            assert os.path.exists(f"resource/QChatGPT/{file}")
