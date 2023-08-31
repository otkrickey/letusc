from os import environ, path

from dotenv import load_dotenv


def env(key: str) -> str:
    load_dotenv(verbose=True)
    dotenv_path = path.abspath(path.join(path.dirname(__file__), "../../.env"))
    load_dotenv(dotenv_path)
    val = environ.get(key)
    if not isinstance(val, str):
        raise ValueError(f"env {key} is not set")
    return val


def env_bool(key: str) -> bool:
    try:
        res = env(key)
    except ValueError:
        return False
    true_list = ["1", "True", "true", "TRUE", "t", "T", "y", "Y", "yes", "Yes", "YES"]
    if res in true_list:
        return True
    return False


__all__ = [
    "env",
    "env_bool",
]
