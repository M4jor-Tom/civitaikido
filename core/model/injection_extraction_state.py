from enum import Enum

class InjectionExtractionState(Enum):
    INIT: str = "INIT"
    BROWSER_OPEN: str = "BROWSER_OPEN"
    PAGE_PREPARED: str = "PAGE_PREPARED"
    PROMPT_INJECTED: str = "PROMPT_INJECTED"
    IMAGES_GENERATED: str = "IMAGES_GENERATED"
    IMAGES_EXTRACTED: str = "IMAGES_EXTRACTED"
    TERMINATED: str = "TERMINATED"
