#!./python

import re
import lxml.etree as ET
from fastapi import FastAPI, HTTPException, UploadFile, File
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio
import requests

from pydantic import BaseModel, computed_field

# ANSI color codes for colored output
COLOR_OK = "\033[92m"       # Green
COLOR_ERROR = "\033[91m"    # Red
COLOR_WARNING = "\033[93m"  # Yellow
COLOR_RESET = "\033[0m"     # Reset color

civitai_selectors: dict[str, str] = {
    'positivePromptArea': "#input_prompt",
    'negativePromptArea': "#input_negativePrompt",
    'cfgScaleHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div:nth-child(1) > div > div.mantine-Slider-root.flex-1.mantine-15k342w > input[type=hidden]",
    'cfgScaleTextInput': "#mantine-rh",
    'samplerHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div.mantine-InputWrapper-root.mantine-Select-root.mantine-1m3pqry > div > input[type=hidden]",
    'samplerSearchInput': "#input_sampler",
    'stepsHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div:nth-child(3) > div > div.mantine-Slider-root.flex-1.mantine-15k342w > input[type=hidden]",
    'stepsTextInput': "#mantine-rj"
}

# Global variables
browser = None
civitai_page = None
signed_in_civitai_generation_url: str = None
first_session_preparation: bool = True
civitai_generation_url: str = 'https://civitai.com/generate'
civitai_user_page_url: str = 'https://civitai.com/user/account'
browser_ready_event = asyncio.Event()
global_timeout: int = 60000

model_search_input_selector: str = 'div > div > div > div > div > div > input[placeholder="Search Civitai"]'

class URLInput(BaseModel):
    url: str

class Resource(BaseModel):
    hash: str

class LoraWheight(BaseModel):
    lora: Resource
    wheight: float

class Prompt(BaseModel):
    base_model: Resource
    loraWheights: list[LoraWheight]
    embeddings: list[Resource]
    vae: Resource | None
    positive_prompt_text: str
    negative_prompt_text: str | None
    image_width_px: int
    image_height_px: int
    generation_steps: int
    sampler_name: str
    cfg_scale: float
    seed: str
    clip_skip: int

    @computed_field
    @property
    def ratio_selector_text(self) -> str | None:
        if self.image_width_px == 832 and self.image_height_px == 1216:
            return 'Portrait832x1216'
        elif self.image_width_px == 1216 and self.image_height_px == 832:
            return 'Landscape1216x832'
        elif self.image_width_px == 1024 and self.image_height_px == 1024:
            return 'Square1024x1024'
        return None

def log_wait(message: str):
        print("⏳ [WAIT] " + message)

def log_done(message: str):
        print("✅ [DONE] " + message)

def log_skip(message: str):
        print("⚠️ [SKIP] " + message)

async def try_action(action_name: str, callback):
    try:
        log_wait(action_name)
        await callback()
        log_done(action_name)
    except Exception as e:
        log_skip(action_name + ": " + str(e))

async def click_if_visible(action_name: str, locator):
    if await locator.is_visible():
        await locator.click()
        log_done("Clicked locator for " + action_name)
    else:
        log_skip("Locator for " + action_name + " not visible")

def fetch_xsd(xsd_url: str) -> ET.XMLSchema:
    """Fetches an XSD file from a URL and returns an XMLSchema object.

    Args:
        xsd_url: URL of the XSD schema.

    Returns:
        XMLSchema object if successfully fetched, else None.
    """
    try:
        response = requests.get(xsd_url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP failures

        xsd_tree = ET.XML(response.content)
        return ET.XMLSchema(xsd_tree)
    except requests.RequestException as e:
        print(f"{COLOR_ERROR}[ERROR] Failed to fetch XSD from {xsd_url}: {e}{COLOR_RESET}")
        return None
    except ET.XMLSyntaxError as e:
        print(f"{COLOR_ERROR}[ERROR] Invalid XSD format from {xsd_url}: {e}{COLOR_RESET}")
        return None

async def remove_cookies():
    async def interact():
        await civitai_page.get_by_text("Customise choices").wait_for(state="visible", timeout=global_timeout)
        await civitai_page.get_by_text("Customise choices").click()
        await civitai_page.get_by_text("Save preferences").click()
    await try_action("remove_cookies", interact)

async def enter_parameters_perspective():
    async def interact():
        await civitai_page.locator('div[title]').first.click()
        await civitai_page.locator('a[href="/user/account"]').first.click()
    await try_action("enter_parameters_perspective", interact)

async def enable_mature_content():
    async def interact():
        await civitai_page.locator('//*[text()="Show mature content")').first.click()
        await civitai_page.locator('//*[text()="Blur mature content")').first.click()
        # await civitai_page.locator('//*[text()="PG")').first.click()
        await civitai_page.locator('//*[text()="Safe for work. No naughty stuff")').first.click()
        # await civitai_page.locator('//*[text()="PG-13")').first.click()
        await civitai_page.locator('//*[text()="Revealing clothing, violence, or light gore")').first.click()
        # await civitai_page.locator('//*[text()="R")').first.click()
        await civitai_page.locator('//*[text()="Adult themes and situations, partial nudity, graphic violence, or death")').first.click()
        # await civitai_page.locator('//*[text()="X")').first.click()
        await civitai_page.locator('//*[text()="Graphic nudity, adult objects, or settings")').first.click()
        # await civitai_page.locator('//*[text()="XXX")').first.click()
        await civitai_page.locator('//*[text()="Overtly sexual or disturbing graphic content")').first.click()
    await try_action("enable_mature_content", interact)

async def enter_generation_perspective():
    async def interact():
        await civitai_page.locator('button[data-activity="create:navbar"]').first.click()
        await civitai_page.locator('a[href="/generate"]').first.click()
    await try_action("enter_generation_perspective", interact)
    # await civitai_page.goto(civitai_generation_url)

async def skip_getting_started():
    async def interact():
        await civitai_page.get_by_role("button", name="Skip").wait_for(state="visible", timeout=global_timeout)
        await civitai_page.get_by_role("button", name="Skip").click()
    await try_action("skip_getting_started", interact)

async def confirm_start_generating_yellow_button():
    await click_if_visible("confirm_start_generating_yellow_button", civitai_page.get_by_role("button", name="I Confirm, Start Generating"))

async def claim_buzz():
    await click_if_visible("claim_buzz", civitai_page.locator('button:has-text("Claim 25 Buzz")'))

async def prepare_session(first_session_preparation: bool):
    await remove_cookies()
    if first_session_preparation:
        await skip_getting_started()
    await confirm_start_generating_yellow_button()
    await claim_buzz()
    if first_session_preparation:
        await enter_parameters_perspective()
        await enable_mature_content()
    await enter_generation_perspective()

async def init_browser():
    """Initializes the browser when the URL is set."""
    global browser, civitai_page, signed_in_civitai_generation_url, first_session_preparation

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
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        ignore_https_errors=True,
        timezone_id="America/New_York",
        permissions=["geolocation"],
    )

    civitai_page = await context.new_page()

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
    await prepare_session(first_session_preparation)

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

@app.post("/open_browser")
async def open_browser(data: URLInput, ask_first_session_preparation: bool):
    """Sets the signed-in CivitAI generation URL and unblocks the browser startup."""
    global signed_in_civitai_generation_url, first_session_preparation

    if not data.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    first_session_preparation = ask_first_session_preparation
    signed_in_civitai_generation_url = data.url
    return {"message": "URL set successfully; Session prepared for xml injection", "url": signed_in_civitai_generation_url}

def parse_prompt(xml_root) -> Prompt:
    # Extract base model information
    base_model_hash = xml_root.find(".//base-model/hash").text
    base_model = Resource(hash=base_model_hash)

    # Extract Loras and their weights
    loraWheights = []
    for lora_elem in xml_root.findall(".//resources/lora"):
        lora_hash = lora_elem.find("hash").text
        lora_weight = float(lora_elem.find("wheight").text)
        loraWheights.append(LoraWheight(
            lora=Resource(hash=lora_hash),
            wheight=lora_weight
        ))

    # Extract embeddings
    embeddings = []
    for embedding_elem in xml_root.findall(".//resources/embedding"):
        embedding_hash = embedding_elem.find("hash").text
        embeddings.append(Resource(hash=embedding_hash))

    # Extract VAE (optional)
    vae_elem = xml_root.find(".//vae")
    vae = None
    if vae_elem is not None:
        vae_hash = vae_elem.find("hash").text
        vae = Resource(hash=vae_hash)

    # Extract other parameters
    positive_prompt_text = xml_root.find(".//positive-prompt").text
    negative_prompt_text = xml_root.find(".//negative-prompt").text if xml_root.find(".//negative-prompt") is not None else None
    image_width_px = int(xml_root.find(".//width").text)
    image_height_px = int(xml_root.find(".//height").text)
    generation_steps = int(xml_root.find(".//steps").text)
    sampler_name = xml_root.find(".//sampler").text
    cfg_scale = float(xml_root.find(".//cfg-scale").text)
    seed = xml_root.find(".//seed").text
    clip_skip = int(xml_root.find(".//clip-skip").text)

    # Create and return the parsed Prompt object
    return Prompt(
        base_model=base_model,
        loraWheights=loraWheights,
        embeddings=embeddings,
        vae=vae,
        positive_prompt_text=positive_prompt_text,
        negative_prompt_text=negative_prompt_text,
        image_width_px=image_width_px,
        image_height_px=image_height_px,
        generation_steps=generation_steps,
        sampler_name=sampler_name,
        cfg_scale=cfg_scale,
        seed=seed,
        clip_skip=clip_skip
    )

async def add_resource_by_hash(resource_hash: str):
    log_wait("add_resource_by_hash: " + resource_hash)
    await civitai_page.locator(model_search_input_selector).fill(resource_hash)
    await asyncio.sleep(5)
    await civitai_page.locator("img[src][class][style][alt][loading]").last.click(force=True)
    await civitai_page.locator('button[data-activity="create:model"]').wait_for(timeout=global_timeout)
    await civitai_page.locator('button[data-activity="create:model"]').click()
    await enter_generation_perspective()
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

async def generate():
    log_wait("generate")
    await civitai_page.get_by_role("button", name="Generate").click()
    log_done("generate")

async def inject(prompt: Prompt):
    await add_resource_by_hash(prompt.base_model.hash)
    await open_additional_resources_accordion()
    await asyncio.sleep(2)
    for loraWheight in prompt.loraWheights:
        await add_resource_by_hash(loraWheight.lora.hash)
        await set_lora_weight(loraWheight.wheight)
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
    await set_seed(prompt.seed)

@app.post("/inject_prompt")
async def inject_prompt(file: UploadFile = File(...)):
    """Validates an uploaded XML file against an XSD schema from a given URL.

    Returns:
        A JSON response indicating whether the XML is valid or not.
    """
    try:
        # Read XML content
        xml_content = await file.read()
        xml_tree = ET.ElementTree(ET.fromstring(xml_content))
        root = xml_tree.getroot()

        # Extract xsi:noNamespaceSchemaLocation (URL or file path)
        xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"
        xsd_location = root.attrib.get(f"{{{xsi_ns}}}noNamespaceSchemaLocation")

        # Parse the XSD schema
        if xsd_location.startswith(("http://", "https://")):
            xsd_schema = fetch_xsd(xsd_location)
            if not xsd_schema:
                print("Failed to fetch the XSD")

        # Validate XML against the schema
        if xsd_schema.validate(xml_tree):
            print("XML is valid against the provided XSD")
        else:
            errors = xsd_schema.error_log
            print("XML validation failed: " + errors.last_error)
        
        prompt = parse_prompt(root)
        print(prompt.model_dump())
        await inject(prompt)

    except ET.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("civitaikido:app", host="127.0.0.1", port=8000, reload=True)
