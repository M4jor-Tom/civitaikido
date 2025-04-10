from pydantic import BaseModel

from core.model.file_scene_dto import FileSceneDto
from core.model.injection_extraction_state import InjectionExtractionState


class Scene(BaseModel):
    session_id: str
    civitai_url: str | None
    injected_file: FileSceneDto | None
    injection_extraction_state: InjectionExtractionState
