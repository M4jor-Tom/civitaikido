from pydantic import BaseModel

from core.model.injection_extraction_state import InjectionExtractionState


class Scene(BaseModel):
    session_id: str
    civitai_url: str
    injection_extraction_state: InjectionExtractionState
