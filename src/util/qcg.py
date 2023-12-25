import os
import logging

from . import system


def ensure_qchatgpt(
    pwd: str = ".",
):
    """
    Ensure QChatGPT is setup.

    Args:
        cwd (str): Working directory.
    """
    logging.info("Ensuring QChatGPT is setup...")

    if not os.path.exists(pwd+"/QChatGPT"):
        setup_qchatgpt(pwd=pwd)

    logging.info("QChatGPT is setup.")

    return


def setup_qchatgpt(
    branch: str = None,
    commit: str = None,
    pwd: str = ".",
):
    """
    Setup QChatGPT from GitHub.

    Args:
        cwd (str): Working directory.
    """
    logging.info("Setting up QChatGPT...")

    # Create the directory
    if not os.path.exists(pwd):
        os.makedirs(pwd)

    # 从环境变量中获取分支和提交
    if branch is None:
        branch = os.environ['BRANCH'] if 'BRANCH' in os.environ else "master"

    if commit is None:
        commit = os.environ['COMMIT'] if 'COMMIT' in os.environ else "HEAD"

    # Clone the repo
    stdout, stderr = system.run_command(
        command=f"git clone https://github.com/RockChinQ/QChatGPT.git",
        cwd=pwd,
        timeout=120,
    )

    logging.info(stdout)
    logging.info(stderr)

    # Checkout the branch
    stdout, stderr = system.run_command(
        command=f"git checkout {branch}",
        cwd=pwd+"/QChatGPT",
        timeout=120,
    )

    logging.info(stdout)
    logging.info(stderr)

    # Checkout the commit
    stdout, stderr = system.run_command(
        command=f"git checkout {commit}",
        cwd=pwd+"/QChatGPT",
        timeout=120,
    )

    logging.info(stdout)
    logging.info(stderr)

    # Install dependencies
    stdout, stderr = system.run_command(
        command=f"pip install -r requirements.txt",
        cwd=pwd+"/QChatGPT",
        timeout=120,
    )

    logging.info("QChatGPT setup complete.")

    return


def cleanup_qchatgpt(
    pwd: str = ".",
):
    """
    Cleanup QChatGPT.

    Args:
        pwd (str): Working directory.
    """
    logging.info("Cleaning up QChatGPT...")
    # Remove the repo
    stdout, stderr = system.run_command(
        command=f"rm -rf QChatGPT",
        cwd=pwd,
        timeout=120,
    )

    logging.info(stdout)
    logging.info(stderr)

    logging.info("QChatGPT cleanup complete.")

    return
