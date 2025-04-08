import logging
from core.model.injection_extraction_state import InjectionExtractionState

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, injection_extraction_state: InjectionExtractionState):
        self.injection_extraction_state: InjectionExtractionState = injection_extraction_state

    def update_injection_extraction_state(self, new_state: InjectionExtractionState):
        logger.info(f"[STATE TRANSITION]: from {self.injection_extraction_state} to {new_state}")
        self.injection_extraction_state = new_state
