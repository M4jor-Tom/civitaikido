from src.model.injection_extraction_state import InjectionExtractionState

class StateManager:
    injection_extraction_state: InjectionExtractionState
    def __init__(self, injection_extraction_state: InjectionExtractionState):
        self.injection_extraction_state = injection_extraction_state
