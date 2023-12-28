import logging
import os

import pytest
import coverage

from src.util import coverage as cov 

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler()])

    if os.path.exists("resource/"):
        os.system("rm -rf resource/")
    if os.path.exists("report/"):
        os.system("rm -rf report/")

    # 打印所有环境变量
    for key, value in os.environ.items():
        print(f"env: {key}={value}")

    test_dirs = "src"
    if 'TEST_DIRS' in os.environ:
        test_dirs = os.environ['TEST_DIRS']
    dirs = test_dirs.split(':')

    # 清除覆盖率数据
    cov.clean_coverage_data(cwd="resource/QChatGPT")

    print(f"Running tests in {dirs}")
    
    code = pytest.main(dirs)

    # 生成覆盖率报告
    cov.combine_coverage_data(cwd="resource/QChatGPT")
    cov.copy_coverage_html(cwd="resource/QChatGPT", dest="report/coverage")

    exit(code)