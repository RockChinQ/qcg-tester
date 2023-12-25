import os
import logging

from . import system


def setup_qchatgpt(
    branch: str = "master",
    commit: str = "HEAD",
    pwd: str = ".",
):
    """
    Setup QChatGPT from GitHub.

    Args:
        branch (str): Branch name.
        commit (str): Commit hash.
    """
    logging.info("Setting up QChatGPT...")

    if not os.path.exists(pwd):
        os.makedirs(pwd)

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
