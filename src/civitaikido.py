import lxml.etree as ET
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio

from src.config.constant import *
from src.model import Prompt, URLInput
from src.service import ReadXmlPromptService, PrepareCivitaiPage, ImageExtractor
from src.util import log_wait, log_done, log_skip, try_action

read_xml_prompt_service: ReadXmlPromptService = ReadXmlPromptService()

# Global variables
browser = None
civitai_page = None
signed_in_civitai_generation_url: str | None = None
first_session_preparation: bool = True
browser_ready_event = asyncio.Event()
prepare_civitai_page: PrepareCivitaiPage | None = None
image_extractor: ImageExtractor | None = None
browser_initialized: bool = False
generation_default_dir: str = "civitai/images/generation"

async def init_browser():
    """Initializes the browser when the URL is set."""
    global browser, civitai_page, signed_in_civitai_generation_url, first_session_preparation, prepare_civitai_page, image_extractor, browser_initialized

    log_wait("Browser to initialise...")

    # Wait until an URL is set
    while signed_in_civitai_generation_url is None:
        await asyncio.sleep(1)

    log_done("URL received: " + signed_in_civitai_generation_url)

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
    context.set_default_timeout(120000)

    civitai_page = await context.new_page()
    # await civitai_page.add_init_script(path="stealth.m#in.js")

    # Load the provided URL
    await civitai_page.goto(signed_in_civitai_generation_url)

    await civitai_page.wait_for_selector("#__next", timeout=global_timeout)

    try:
        await civitai_page.wait_for_load_state("domcontentloaded", timeout=global_timeout)
    except Exception:
        log_skip("Page load state took too long, continuing anyway.")

    await asyncio.sleep(5)

    # Apply stealth mode
    await stealth_async(civitai_page)

    log_done("Browser initialized with anti-bot protections")
    browser_ready_event.set()  # Notify that the browser is ready
    prepare_civitai_page = PrepareCivitaiPage(civitai_page)
    image_extractor = ImageExtractor(civitai_page)
    await prepare_civitai_page.prepare_session(first_session_preparation)
    browser_initialized = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function that starts FastAPI without blocking Swagger and browser startup."""
    print("🚀 FastAPI is starting...")

    # Start the browser initialization in a background task
    asyncio.create_task(init_browser())

    yield  # Allow FastAPI to run

    # Shutdown sequence
    if browser:
        await civitai_page.close()
        await browser.close()
        print("🛑 Browser closed!")

app = FastAPI(lifespan=lifespan)

async def open_browser(data: URLInput, ask_first_session_preparation: bool, await_browser_initialized: bool):
    """Sets the signed-in CivitAI generation URL and unblocks the browser startup."""
    global signed_in_civitai_generation_url, first_session_preparation

    if not data.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    first_session_preparation = ask_first_session_preparation
    signed_in_civitai_generation_url = data.url
    log_wait("message: URL set successfully; Session prepared for xml injection, url: " + signed_in_civitai_generation_url)
    if await_browser_initialized:
        while not browser_initialized:
            await asyncio.sleep(1)

@app.post("/open_browser")
async def rest_open_browser(data: URLInput, ask_first_session_preparation: bool):
    await open_browser(data, ask_first_session_preparation, False)
    return {"message": "Browser prepared", "url": data.url}

async def add_resource_by_hash(resource_hash: str):
    global prepare_civitai_page
    log_wait("add_resource_by_hash: " + resource_hash)
    await civitai_page.locator(model_search_input_selector).fill(resource_hash)
    await asyncio.sleep(5)
    await civitai_page.locator("img[src][class][style][alt][loading]").last.click(force=True)
    await civitai_page.locator('button[data-activity="create:model"]').wait_for(timeout=global_timeout)
    await civitai_page.locator('button[data-activity="create:model"]').click()
    await prepare_civitai_page.enter_generation_perspective()
    log_done("add_resource_by_hash: " + resource_hash)

async def open_additional_resources_accordion():
    log_wait("open_additional_resources_accordion")
    await civitai_page.locator("//*[text()='Additional Resources']").click()
    log_done("open_additional_resources_accordion")

async def set_lora_weight(lora_weight: float):
    log_wait("set_lora_weight: " + str(lora_weight))
    await civitai_page.locator("(//*[div/div/div/div/text()='Additional Resources']/following-sibling::*//input[@type][@max][@min][@step][@inputmode])[1]").fill(str(lora_weight))
    log_done("set_lora_weight: " + str(lora_weight))

async def write_positive_prompt(positive_text_prompt: str):
    log_wait("write_positive_prompt")
    await civitai_page.get_by_role("textbox", name="Your prompt goes here...").fill(positive_text_prompt)
    log_done("write_positive_prompt")

async def write_negative_prompt(negative_text_prompt: str):
    async def interact():
        await civitai_page.get_by_role("textbox", name="Negative Prompt").fill(negative_text_prompt)
    await try_action("write_negative_prompt", interact)

async def set_ratio_by_text(ratio_text: str):
    log_wait("set_ratio_by_text: " + ratio_text)
    await civitai_page.locator("label").filter(has_text=ratio_text).click()
    log_done("set_ratio_by_text: " + ratio_text)

async def toggle_image_properties_accordion():
    log_wait("toggle_image_properties_accordion")
    await civitai_page.get_by_role("button", name="Advanced").click()
    log_done("toggle_image_properties_accordion")

async def set_cfg_scale(cfg_scale: float):
    async def interact():
        await civitai_page.locator("#input_cfgScale-label + div > :nth-child(2) input").wait_for(timeout=global_timeout)
        await civitai_page.locator("#input_cfgScale-label + div > :nth-child(2) input").fill(str(cfg_scale))
    await try_action('set_cfg_scale: ' + str(cfg_scale), interact)

async def set_sampler(sampler: str):
    log_wait("set_sampler: " + sampler)
    await civitai_page.locator("#input_sampler").click()
    await civitai_page.locator("//div[@role='combobox']/following-sibling::div//div[text()='" + sampler + "']").click()
    log_done("set_sampler: " + sampler)

async def set_steps(steps: int):
    log_wait("set_steps: " + str(steps))
    await civitai_page.locator("#input_steps-label + div > :nth-child(2) input").fill(str(steps))
    log_done("set_steps: " + str(steps))

async def set_seed(seed: str):
    log_wait("set_seed: " + seed)
    await civitai_page.get_by_role("textbox", name="Random").fill(seed)
    log_done("set_seed: " + seed)

async def give_no_tips():
    log_wait("give_no_tips")
    await civitai_page.locator(generation_info_button_selector).click()
    await civitai_page.locator(creator_tip_selector).fill("0%")
    await civitai_page.locator(civitai_tip_selector).fill("0%")
    log_done("give_no_tips")

@app.post("/generate_till_no_buzz")
async def generate_till_no_buzz():
    log_wait("generate_till_no_buzz")
    log_wait("launch_all_generations")
    await give_no_tips()
    buzz_remain: bool = True
    while buzz_remain is True:
        buzz_remain: bool = (await civitai_page.locator(no_more_buzz_triangle_svg_selector).count()) == 0
        print("buzz_remain: " + str(buzz_remain))
        if buzz_remain:
            await civitai_page.locator(generation_button_selector).wait_for(timeout=120000)
            await civitai_page.locator(generation_button_selector).click()
            await asyncio.sleep(3)
    log_done("launch_all_generations")
    await civitai_page.locator(all_jobs_done_selector).wait_for(timeout=120000)
    log_done("generate_till_no_buzz")

async def inject(prompt: Prompt, inject_seed: bool):
    await add_resource_by_hash(prompt.base_model.hash)
    await open_additional_resources_accordion()
    await asyncio.sleep(2)
    for lora_weight in prompt.lora_weights:
        await add_resource_by_hash(lora_weight.lora.hash)
        await set_lora_weight(lora_weight.weight)
    for embedding in prompt.embeddings:
        await add_resource_by_hash(embedding.hash)
    if prompt.vae is not None:
        await add_resource_by_hash(prompt.vae.hash)
    await write_positive_prompt(prompt.positive_prompt_text)
    if prompt.negative_prompt_text is not None:
        await write_negative_prompt(prompt.negative_prompt_text)
    ratio_selector_text: str | None = prompt.ratio_selector_text
    if ratio_selector_text is not None:
        await set_ratio_by_text(ratio_selector_text)
    await toggle_image_properties_accordion()
    await set_cfg_scale(prompt.cfg_scale)
    await set_sampler(prompt.sampler_name)
    await set_steps(prompt.generation_steps)
    if prompt.seed is not None and inject_seed:
        await set_seed(prompt.seed)

@app.post("/inject_prompt")
async def inject_prompt(file: UploadFile = File(...), inject_seed: bool = False):
    """Validates an uploaded XML file against an XSD schema from a given URL.

    Returns:
        A JSON response indicating whether the XML is valid or not.
    """
    global generation_default_dir
    generation_default_dir += "/" + str(file.filename).split('.xml')[0]
    try:
        # Read XML content
        xml_content = await file.read()
        xml_tree = ET.ElementTree(ET.fromstring(xml_content))
        root = xml_tree.getroot()
        
        prompt = read_xml_prompt_service.parse_prompt(root)
        print(prompt.model_dump())
        await inject(prompt, inject_seed)
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
    await open_browser(URLInput(url=session_url), True, True)
    await inject_prompt(file, inject_seed)
    await generate_till_no_buzz()
    await extract_images(generation_default_dir)
