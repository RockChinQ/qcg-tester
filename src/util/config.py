import logging
import importlib

def set_config(key: str, value: str, cwd: str = "."):
    """
    把 赋值 写到 config.py 末尾以覆盖默认值
    """

    with open(f"{cwd}/config.py", "a") as f:
        f.write(f"\n{key} = {value}\n")

    logging.info(f"Set {key} to {value}.")
    return

def get_config(key: str, cwd: str = "."):
    """
    从 config.py 中读取配置
    """

    config = importlib.import_module("config", cwd)

    logging.info(f"Get {key} from config.py.")

    return getattr(config, key)