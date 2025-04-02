from enum import Enum

class Role(Enum):
    buzz_runner = "buzz_runner"
    injector_extractor = "injector_extractor"

def role_from_value(value: str) -> Role:
    for profile in Role:
        if profile.value == value:
            return profile
    raise ValueError(f"Unknown profile value: {value}")

def get_available_roles() -> list[str]:
    return [e.name for e in Role]
