from os import path, environ
from dotenv import load_dotenv


def env(key: str) -> str:
    load_dotenv(verbose=True)
    dotenv_path = path.abspath(path.join(path.dirname(__file__), "../../.env"))
    load_dotenv(dotenv_path)
    val = environ.get(key)
    if not isinstance(val, str):
        raise ValueError(f"env {key} is not set")
    return val