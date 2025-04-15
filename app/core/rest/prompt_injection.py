import lxml.etree as et
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from core.config import GENERATION_DEFAULT_DIR
from core.constant import low_layer
from core.model import FileStateDto, build_generation_path_from_generation_dir_and_file
from core.provider import get_prompt_tree_builder, get_prompt_builder, get_prompt_injector
from core.service import PromptTreeBuilder, PromptBuilder, PromptInjector

prompt_injection_router = APIRouter()

@prompt_injection_router.post("/inject_prompt", tags=[low_layer])
async def inject_prompt(file: UploadFile = File(...), inject_seed: bool = False,
                        prompt_tree_builder: PromptTreeBuilder = Depends(get_prompt_tree_builder),
                        prompt_builder: PromptBuilder = Depends(get_prompt_builder),
                        prompt_injector: PromptInjector = Depends(get_prompt_injector)):
    """Validates an uploaded XML file against an XSD schema from a given URL.

    Returns:
        A JSON response indicating whether the XML is valid or not.
    """
    try:
        root = await prompt_tree_builder.build_prompt_tree(file)
        prompt = prompt_builder.build_from_xml(root)
        await prompt_injector.inject(prompt, inject_seed)
    except et.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
