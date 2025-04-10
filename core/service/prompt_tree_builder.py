from fastapi import File
import lxml.etree as et

from core.model import FileSceneDto


class PromptTreeBuilder:
    def __init__(self):
        self.file_dto: FileSceneDto or None = None
    async def build_prompt_tree(self, file: File, file_dto: FileSceneDto) -> any:
        self.file_dto = file_dto
        xml_content = await file.read()
        xml_tree = et.ElementTree(et.fromstring(xml_content))
        return xml_tree.getroot()
