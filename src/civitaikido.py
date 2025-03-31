import lxml.etree as ET
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio
import logging

from src.service import *
from src.constant import *

logger = logging.getLogger(__name__)

# Services
browser_manager: BrowserManager = BrowserManager()
prompt_builder: PromptBuilder = PromptBuilder()
xml_parser: XmlParser = XmlParser()
civitai_page_preparator = CivitaiPagePreparator(browser_manager)
image_generator = ImageGenerator(browser_manager)
image_extractor = ImageExtractor(browser_manager)
prompt_injector = PromptInjector(browser_manager, civitai_page_preparator)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function that starts FastAPI without blocking Swagger and browser startup."""
    logger.info("🚀 FastAPI is starting...")

    # Start the browser initialization in a background task
    asyncio.create_task(browser_manager.init_browser())

    yield  # Allow FastAPI to run
    await browser_manager.shutdown_if_possible()

app = FastAPI(lifespan=lifespan)

@app.post("/open_browser")
async def open_browser(civitai_connection_url: str, ask_first_session_preparation: bool):
    await browser_manager.open_browser(civitai_connection_url)
    await civitai_page_preparator.prepare_civitai_page(ask_first_session_preparation)
    return {"message": "Browser prepared", "url": civitai_connection_url}

@app.post("/generate_till_no_buzz")
async def generate_till_no_buzz():
    await image_generator.generate_till_no_buzz()

@app.post("/inject_prompt")
async def inject_prompt(file: UploadFile = File(...), inject_seed: bool = False):
    """Validates an uploaded XML file against an XSD schema from a given URL.

    Returns:
        A JSON response indicating whether the XML is valid or not.
    """
    try:
        root = await xml_parser.parse_xml(file)
        prompt = prompt_builder.build_from_xml(root)
        logger.info(prompt.model_dump())
        await prompt_injector.inject(prompt, inject_seed)
    except ET.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/extract_images")
async def extract_images(extraction_dir: str = generation_default_dir):
    await image_extractor.save_images_from_page(extraction_dir)

@app.post("/inject_generate_extract")
async def inject_generate_extract(
        session_url: str = Form(...),
        file: UploadFile = File(...),
        inject_seed: bool = False
    ):
    await browser_manager.open_browser(session_url)
    await civitai_page_preparator.prepare_civitai_page(True)
    await prompt_injector.inject(prompt_builder.build_from_xml(await xml_parser.parse_xml(file)), inject_seed)
    await image_generator.generate_till_no_buzz()
    await image_extractor.save_images_from_page(generation_default_dir + "/" + str(file.filename).split('.xml')[0])
