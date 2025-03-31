import os
from pathlib import Path
from dotenv import load_dotenv

class Env:
    def __init__(self, env_file: str | None = ".env") -> None:
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)

    def get(self, key: str, default: str | None = None) -> str:
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing env var: {key}")
        return value

    def get_int(self, key: str, default: int | None = None) -> int:
        val = os.getenv(key)
        if val is None:
            if default is not None:
                return default
            raise ValueError(f"Missing env var: {key}")
        return int(val)

    def get_bool(self, key: str, default: bool = False) -> bool:
        val = os.getenv(key)
        return val.lower() in {"1", "true", "yes", "on"} if val else default
