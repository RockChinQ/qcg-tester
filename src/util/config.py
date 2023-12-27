import logging
import sys
import importlib

def set_config(key: str, value: str, cwd: str = "."):
    """
    把 赋值 写到 config.py 末尾以覆盖默认值
    """

    with open(f"{cwd}/config.py", "a") as f:
        f.write(f"\n{key} = {value}\n")

    logging.info(f"Set {key} to {value}.")
    return

def load_module_from_path(module_name, filepath):
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def get_config(key: str, cwd: str = "."):
    """
    从 config.py 中读取配置
    """
    logging.info(f"Get {key} from {cwd}/config.py.")

    config = load_module_from_path("config", f"{cwd}/config.py")

    return getattr(config, key)

def ensure_config(key: str, value: str, cwd: str = "."):
    """
    确保配置被设置
    """

    if not get_config(key, cwd) or get_config(key, cwd) != eval(value):
        set_config(key, value, cwd)

    return
