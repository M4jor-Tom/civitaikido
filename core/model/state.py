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

def build_revived_state(dead_state: State, max_revives: int) -> State:
    injection_extraction_state_after_revive: InjectionExtractionState = dead_state.injection_extraction_state
    if dead_state.revives > max_revives:
        injection_extraction_state_after_revive = InjectionExtractionState.TERMINATED
    return State(
        session_id=dead_state.session_id,
        civitai_url=dead_state.civitai_url,
        inject_seed=dead_state.inject_seed,
        revives=dead_state.revives + 1,
        injected_file=dead_state.injected_file,
        injection_extraction_state=injection_extraction_state_after_revive,
        close_browser_when_finished=dead_state.close_browser_when_finished
    )
