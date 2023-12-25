import os
import logging
import time
import asyncio


def run_command(
    command: str,
    cwd: str = None,
    env: dict = None,
    timeout: int = None,
) -> (str, str):
    """
    Run a command.

    Args:
        command (str): Command to run.
        cwd (str): Working directory.
        env (dict): Environment variables.
        timeout (int): Timeout.

    Returns:
        (str, str): stdout and stderr.
    """

    import subprocess
    import shlex

    if cwd is None:
        cwd = os.getcwd()

    if env is None:
        env = os.environ.copy()

    command = shlex.split(command)

    logging.info(f"Running command: {command}")

    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logging.info(f"Command killed: {command}")
    logging.info(f"Command stdout: {stdout}")

    return stdout, stderr

async def run_command_async(
    command: str,
    cwd: str = None,
    env: dict = None,
    timeout: int = None,
) -> (str, str):
    """
    Run a command.

    Args:
        command (str): Command to run.
        cwd (str): Working directory.
        env (dict): Environment variables.
        timeout (int): Timeout.

    Returns:
        (str, str): stdout and stderr.
    """

    import subprocess
    import shlex

    if cwd is None:
        cwd = os.getcwd()

    if env is None:
        env = os.environ.copy()

    command = shlex.split(command)

    logging.info(f"Running command: {command}")

    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=cwd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        stdout, stderr = await process.communicate()

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logging.info(f"Command killed: {command}")
    logging.info(f"Command stdout: {stdout}")

    return stdout, stderr