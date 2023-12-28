import os


def clean_coverage_data(
    cwd: str,
):
    """
    Clean coverage data.

    Args:
        cwd (str): Working directory.
    """

    os.system(f"rm -rf {cwd}/.coverage*")
    os.system(f"rm -rf {cwd}/coverage*")

    os.system(f"rm -rf {cwd}/htmlcov")

    return

def combine_coverage_data(
    cwd: str,
):
    """
    Combine coverage data.

    Args:
        cwd (str): Working directory.
    """

    # 切换到cwd，执行coverage combine
    print(f"cd {cwd} && coverage combine && coverage html")
    os.system(f"cd {cwd} && coverage combine && coverage html")

    return

def copy_coverage_html(
    cwd: str,
    dest: str,
):
    """
    Copy coverage html.

    Args:
        cwd (str): Working directory.
        dest (str): Destination.
    """
    print(f"cp -r {cwd}/htmlcov {dest}")
    if not os.path.exists(dest):
        os.system(f"mkdir -p {dest}")
    os.system(f"cp -r {cwd}/htmlcov {dest}")

    return