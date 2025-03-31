from src.config import Env

env = Env(env_file=".env.d/dev.env")
APP_PORT = env.get_int("APP_PORT", 8000)
PROFILE = env.get("PROFILE", "DEFAULT")
LOGGING_LEVEL = env.get("LOGGING_LEVEL", "DEBUG")
HEADLESS = env.get_bool("HEADLESS", True)
GLOBAL_TIMEOUT = env.get_int("GLOBAL_TIMEOUT", 300000)
GENERATION_DEFAULT_DIR = env.get("GENERATION_DEFAULT_DIR", "civitai/images/generation")
