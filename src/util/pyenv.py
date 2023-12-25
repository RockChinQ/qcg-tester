import sys


def assert_python_version(version: str) -> None:
    """Assert that the current Python version is at least `version`."""
    if sys.version_info < tuple(map(int, version.split("."))):
        raise RuntimeError(
            f"Python {version} or later is required, but you are running "
            f"{sys.version.split()[0]}"
        )
