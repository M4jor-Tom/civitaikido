from fastapi import File
import lxml.etree as et

from core.model import FileSceneDto, build_scene_dto_from_file


class PromptTreeBuilder:
    def __init__(self):
        self.file: FileSceneDto or None = None
    async def build_prompt_tree(self, file: File) -> any:
        self.file = build_scene_dto_from_file(file)
        xml_content = await file.read()
        xml_tree = et.ElementTree(et.fromstring(xml_content))
        return xml_tree.getroot()
    