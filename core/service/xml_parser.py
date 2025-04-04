from fastapi import File
import lxml.etree as et

class XmlParser:
    async def parse_xml(self, file: File) -> any:
        xml_content = await file.read()
        xml_tree = et.ElementTree(et.fromstring(xml_content))
        return xml_tree.getroot()
