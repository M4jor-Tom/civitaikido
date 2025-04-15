import logging

from core.model import State, InjectionExtractionState

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.state: State | None = None

    def update_injection_extraction_state(self, new_state: InjectionExtractionState) -> None:
        if self.state:
            logger.info(f"[STATE TRANSITION]: {self.state.injection_extraction_state.value} => {new_state.value}")
            self.state.injection_extraction_state = new_state
        else:
            raise ValueError("StateManager::state is None")
