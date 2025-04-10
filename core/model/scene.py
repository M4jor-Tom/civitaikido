from pydantic import BaseModel

from core.model.file_scene_dto import FileSceneDto
from core.model.injection_extraction_state import InjectionExtractionState


class Scene(BaseModel):
    session_id: str
    civitai_url: str
    injected_file: FileSceneDto or None
    injection_extraction_state: InjectionExtractionState
