import lxml.etree as ET
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio
import logging

from src.model import URLInput
from src.service import PromptBuilder, CivitaiPagePreparator, ImageExtractor, PromptInjector, XmlParser
from src.constant import *

logger = logging.getLogger(__name__)

# Global variables
browser = None
civitai_page = None
signed_in_civitai_generation_url: str | None = None
first_session_preparation: bool = True
browser_ready_event = asyncio.Event()
browser_initialized: bool = False
generation_default_dir: str = "civitai/images/generation"

# Services
civitai_page_preparator: CivitaiPagePreparator | None = None
image_extractor: ImageExtractor | None = None
prompt_injector: PromptInjector | None = None
prompt_builder: PromptBuilder = PromptBuilder()
xml_parser: XmlParser = XmlParser()

async def init_browser():
    """Initializes the browser when the URL is set."""
    global browser, civitai_page, signed_in_civitai_generation_url, first_session_preparation, \
        civitai_page_preparator, image_extractor, browser_initialized, prompt_injector

    logger.info(WAIT_PREFIX + "Browser to initialise...")

    # Wait until an URL is set
    while signed_in_civitai_generation_url is None:
        await asyncio.sleep(1)

    logger.info(DONE_PREFIX + "URL received: " + signed_in_civitai_generation_url)

    # Start Playwright
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        locale="en-US",
        # locale="fr-FR",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        ignore_https_errors=True,
        # timezone_id="America/New_York",
        timezone_id="Europe/Paris",
        # geolocation={"latitude": 43.1242, "longitude": 5.9280},
        permissions=["geolocation"]
    )
    context.set_default_timeout(global_timeout)

    civitai_page = await context.new_page()
    # await civitai_page.add_init_script(path="stealth.m#in.js")

    # Load the provided URL
    await civitai_page.goto(signed_in_civitai_generation_url)

    await civitai_page.wait_for_selector("#__next", timeout=global_timeout)

    try:
        await civitai_page.wait_for_load_state("domcontentloaded", timeout=global_timeout)
    except Exception:
        logger.warn(SKIP_PREFIX + "Page load state took too long, continuing anyway.")

    await asyncio.sleep(5)

    # Apply stealth mode
    await stealth_async(civitai_page)

    logger.info(DONE_PREFIX + "Browser initialized with anti-bot protections")
    browser_ready_event.set()  # Notify that the browser is ready
    civitai_page_preparator = CivitaiPagePreparator(civitai_page)
    image_extractor = ImageExtractor(civitai_page)
    prompt_injector = PromptInjector(civitai_page, civitai_page_preparator)
    await civitai_page_preparator.prepare_civitai_page(first_session_preparation)
    browser_initialized = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function that starts FastAPI without blocking Swagger and browser startup."""
    logger.info("🚀 FastAPI is starting...")

    # Start the browser initialization in a background task
    asyncio.create_task(init_browser())

    yield  # Allow FastAPI to run

    # Shutdown sequence
    if browser:
        await civitai_page.close()
        await browser.close()
        logger.info("🛑 Browser closed!")

app = FastAPI(lifespan=lifespan)

async def open_browser(data: URLInput, ask_first_session_preparation: bool, await_browser_initialized: bool):
    """Sets the signed-in CivitAI generation URL and unblocks the browser startup."""
    global signed_in_civitai_generation_url, first_session_preparation

    if not data.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    first_session_preparation = ask_first_session_preparation
    signed_in_civitai_generation_url = data.url
    logger.info(WAIT_PREFIX + "message: URL set successfully; Session prepared for xml injection, url: " + signed_in_civitai_generation_url)
    if await_browser_initialized:
        while not browser_initialized:
            await asyncio.sleep(1)

@app.post("/open_browser")
async def rest_open_browser(data: URLInput, ask_first_session_preparation: bool):
    await open_browser(data, ask_first_session_preparation, False)
    return {"message": "Browser prepared", "url": data.url}

@app.post("/generate_till_no_buzz")
async def generate_till_no_buzz():
    await prompt_injector.generate_till_no_buzz()

@app.post("/inject_prompt")
async def inject_prompt(file: UploadFile = File(...), inject_seed: bool = False):
    global prompt_injector
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
    global generation_default_dir
    await open_browser(URLInput(url=session_url), True, True)
    await prompt_injector.inject(prompt_builder.build_from_xml(await xml_parser.parse_xml(file)), inject_seed)
    await prompt_injector.generate_till_no_buzz()
    await image_extractor.save_images_from_page(generation_default_dir + "/" + str(file.filename).split('.xml')[0])
