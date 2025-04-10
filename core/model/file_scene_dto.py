from fastapi import File
from pydantic import BaseModel

class FileSceneDto(BaseModel):
    generation_path: str

def build_generation_path_from_generation_dir_and_file(generation_dir: str, file: File) -> str:
        return generation_dir + "/" + str(file.filename).split('.xml')[0]
