from enum import Enum

class InjectionExtractionState(str, Enum):
    INIT: str = "INIT"
    PROFILE_PREPARED: str = "PROFILE_PREPARED"
    PROMPT_INJECTED: str = "PROMPT_INJECTED"
    IMAGES_GENERATION_LAUNCHED: str = "IMAGES_GENERATION_LAUNCHED"
    IMAGES_EXTRACTED: str = "IMAGES_EXTRACTED"
    TERMINATED: str = "TERMINATED"
