from src.config import Env
from src.model import Role, Profile

env = Env()

ROLE = env.get_role(Role.injector_extractor)
PROFILE = env.get_profile(Profile.PROD)
APP_PORT = env.get_int("APP_PORT", 8000)
LOGGING_LEVEL = env.get("LOGGING_LEVEL", "DEBUG")
HEADLESS = env.get_bool("HEADLESS", True)
GLOBAL_TIMEOUT = env.get_int("GLOBAL_TIMEOUT", 300000)
GENERATION_DEFAULT_DIR = env.get("GENERATION_DEFAULT_DIR", "civitai/images/generation")
