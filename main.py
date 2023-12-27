import logging
import os

import pytest

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler()])

    # 打印所有环境变量
    for key, value in os.environ.items():
        print(f"env: {key}={value}")

    test_dirs = "src"
    if 'TEST_DIRS' in os.environ:
        test_dirs = os.environ['TEST_DIRS']
    dirs = test_dirs.split(':')

    print(f"Running tests in {dirs}")
    
    code = pytest.main(dirs)

    exit(code)