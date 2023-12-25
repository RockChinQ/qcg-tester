import logging
import os

import pytest

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_dirs = "src"
    if 'TEST_DIRS' in os.environ:
        test_dirs = os.environ['TEST_DIRS']
    dirs = test_dirs.split(':')

    print(f"Running tests in {dirs}")
    
    pytest.main(dirs)