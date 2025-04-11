from pydantic import BaseModel

from core.model import FileStateDto, InjectionExtractionState


class State(BaseModel):
    session_id: str
    civitai_url: str | None
    inject_seed: bool
    revives: int
    injected_file: FileStateDto | None
    injection_extraction_state: InjectionExtractionState
    close_browser_when_finished: bool
