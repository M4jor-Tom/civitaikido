from fastapi import File
from pydantic import BaseModel

class FileSceneDto(BaseModel):
    filename: str

    def build_generation_path(self, generation_dir: str) -> str:
        return generation_dir + "/" + str(self.filename).split('.xml')[0]

def build_scene_dto_from_file(file: File) -> FileSceneDto:
    return FileSceneDto(filename=file.filename)
