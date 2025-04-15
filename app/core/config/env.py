import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from core.model import Role, Profile, get_available_profiles, profile_from_value, role_from_value, get_available_roles

logger = logging.getLogger(__name__)

class Env:
    def __init__(self) -> None:
        role = self.get_role(Role.injector_extractor)
        profile = self.get_profile(Profile.PROD)
        env_path = f".env.d/{role.value}.env"
        if profile == Profile.DEV:
            if Path(env_path).exists():
                    load_dotenv(env_path, override=True)
            else:
                raise EnvironmentError(f"environment file: {env_path} does not exist")

    def get(self, key: str, default: str | None = None) -> str:
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing env var: {key}")
        return value

    def get_role(self, default: Role) -> Role:
        return role_from_value(self.get_enum("ROLE", default.value, get_available_roles()))

    def get_profile(self, default: Profile) -> Profile:
        return profile_from_value(self.get_enum("PROFILE", default.value, get_available_profiles()))

    def get_enum(self, key: str, default: str, options: list[str]) -> str:
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing env var: {key}")
        elif value not in options:
            raise ValueError(f"Env var: {key} has invalid value: {value}. Should be within {str(options)}")
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
