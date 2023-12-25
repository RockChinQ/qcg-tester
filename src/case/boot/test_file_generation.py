import os

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
    def test_file_generation(self):
        """ 测试配置文件正常生成 """
        if os.path.exists("resource/"):
            qcg.cleanup_qchatgpt(pwd="resource/")

        qcg.setup_qchatgpt(pwd="resource/")

        for file in file_to_check:
            assert not os.path.exists(f"resource/QChatGPT/{file}")

        system.run_command(
            command="python main.py",
            cwd="resource/QChatGPT",
            timeout=120,
        )

        for file in file_to_check:
            assert os.path.exists(f"resource/QChatGPT/{file}")

