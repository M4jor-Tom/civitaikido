from fastapi import File
import lxml.etree as et


class PromptTreeBuilder:
    async def build_prompt_tree(self, file: File) -> any:
        xml_content = await file.read()
        xml_tree = et.ElementTree(et.fromstring(xml_content))
        return xml_tree.getroot()
