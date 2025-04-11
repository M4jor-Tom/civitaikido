from fastapi import File
from pydantic import BaseModel

from core.model import Prompt


class FileStateDto(BaseModel):
    generation_path: str
    prompt: Prompt

def build_generation_path_from_generation_dir_and_file(generation_dir: str, file: File) -> str:
        return generation_dir + "/" + str(file.filename).split('.xml')[0]
