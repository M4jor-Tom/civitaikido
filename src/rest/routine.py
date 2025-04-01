from fastapi import APIRouter, Depends, Form, File, UploadFile

from src.constant import main
from src.config import GENERATION_DEFAULT_DIR
from src.provider import get_image_generator, get_browser_manager, get_civitai_page_preparator, get_prompt_injector, \
    get_prompt_builder, get_xml_parser, get_image_extractor
from src.service import ImageGenerator, BrowserManager, CivitaiPagePreparator, PromptInjector, PromptBuilder, XmlParser, \
    ImageExtractor

routine_router = APIRouter()

@routine_router.post("/inject_generate_extract", tags=[main])
async def inject_generate_extract(
        session_url: str = Form(...),
        file: UploadFile = File(...),
        inject_seed: bool = False,
        close_browser_when_finished: bool = True,
        browser_manager: BrowserManager = Depends(get_browser_manager),
        civitai_page_preparator: CivitaiPagePreparator = Depends(get_civitai_page_preparator),
        prompt_injector: PromptInjector = Depends(get_prompt_injector),
        prompt_builder: PromptBuilder = Depends(get_prompt_builder),
        xml_parser: XmlParser = Depends(get_xml_parser),
        image_generator: ImageGenerator = Depends(get_image_generator),
        image_extractor: ImageExtractor = Depends(get_image_extractor)
    ):
    await browser_manager.open_browser(session_url)
    await civitai_page_preparator.prepare_civitai_page(True)
    await prompt_injector.inject(prompt_builder.build_from_xml(await xml_parser.parse_xml(file)), inject_seed)
    await image_generator.generate_till_no_buzz()
    await image_extractor.save_images_from_page(GENERATION_DEFAULT_DIR + "/" + str(file.filename).split('.xml')[0])
    if close_browser_when_finished:
        await browser_manager.shutdown_if_possible()
