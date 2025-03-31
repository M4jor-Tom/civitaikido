import lxml.etree as et
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.constant import low_layer
from src.provider import get_xml_parser, get_prompt_builder, get_prompt_injector
from src.service import XmlParser, PromptBuilder, PromptInjector

prompt_injection_router = APIRouter()

@prompt_injection_router.post("/inject_prompt", tags=[low_layer])
async def inject_prompt(file: UploadFile = File(...), inject_seed: bool = False,
                        xml_parser: XmlParser = Depends(get_xml_parser),
                        prompt_builder: PromptBuilder = Depends(get_prompt_builder),
                        prompt_injector: PromptInjector = Depends(get_prompt_injector)):
    """Validates an uploaded XML file against an XSD schema from a given URL.

    Returns:
        A JSON response indicating whether the XML is valid or not.
    """
    try:
        root = await xml_parser.parse_xml(file)
        prompt = prompt_builder.build_from_xml(root)
        await prompt_injector.inject(prompt, inject_seed)
    except et.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
