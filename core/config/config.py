from core.config import Env
from core.model import Role, Profile

env = Env()

ROLE = env.get_role(Role.injector_extractor)
PROFILE = env.get_profile(Profile.PROD)
APP_PORT = env.get_int("APP_PORT", 8000)
LOGGING_LEVEL = env.get("LOGGING_LEVEL", "INFO")
HEADLESS = env.get_bool("HEADLESS", True)
INTERACTION_TIMEOUT = env.get_int("INTERACTION_TIMEOUT", 150000)
IMAGES_GENERATION_TIMEOUT = env.get_int("INTERACTION_TIMEOUT", 300000)
GENERATION_DEFAULT_DIR = env.get("GENERATION_DEFAULT_DIR", "civitai/images/generation")
MAX_REVIVES: int = 5
