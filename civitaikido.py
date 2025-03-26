#!./python

import lxml.etree as ET
from fastapi import FastAPI, HTTPException, UploadFile, File
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio

from pydantic import BaseModel, computed_field

# ANSI color codes for colored output
COLOR_OK = "\033[92m"       # Green
COLOR_ERROR = "\033[91m"    # Red
COLOR_WARNING = "\033[93m"  # Yellow
COLOR_RESET = "\033[0m"     # Reset color

# Global variables
browser = None
civitai_page = None
signed_in_civitai_generation_url: str = None
first_session_preparation: bool = True
browser_ready_event = asyncio.Event()
global_timeout: int = 60000

model_search_input_selector: str = 'div > div > div > div > div > div > input[placeholder="Search Civitai"]'
generation_unavailable_selector: str = "//*[text()='4 jobs in queue']"
remaining_buzz_count_and_no_more_buzz_triangle_svg_selector: str = "//div[text()='Generate']/following-sibling::div/span/div/div/*"
no_more_buzz_triangle_svg_selector: str = "svg.tabler-icon.tabler-icon-alert-triangle-filled"
generation_button_selector: str = "//button//*[text()='Generate']"
generation_info_button_selector: str = "//button[.//*[text()='Generate']]/following-sibling::*"
creator_tip_selector: str = "//div[text()='Creator Tip']//input"
civitai_tip_selector: str = "//div[text()='Civitai Tip']//input"
images_selector: str = "//img[contains(@src,'orchestration.civitai.com')]"

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
    seed: str | None
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
        await civitai_page.locator('//*[text()="Show mature content"]').first.click()
        await civitai_page.locator('//*[text()="Blur mature content"]').first.click()
        # await civitai_page.locator('//*[text()="PG"]').first.click()
        # await civitai_page.locator('//*[text()="Safe for work. No naughty stuff"]').first.click()
        # await civitai_page.locator('//*[text()="PG-13"]').first.click()
        await civitai_page.locator('//*[text()="Revealing clothing, violence, or light gore"]').first.click()
        # await civitai_page.locator('//*[text()="R"]').first.click()
        await civitai_page.locator('//*[text()="Adult themes and situations, partial nudity, graphic violence, or death"]').first.click()
        # await civitai_page.locator('//*[text()="X"]').first.click()
        await civitai_page.locator('//*[text()="Graphic nudity, adult objects, or settings"]').first.click()
        # await civitai_page.locator('//*[text()="XXX"]').first.click()
        await civitai_page.locator('//*[text()="Overtly sexual or disturbing graphic content"]').first.click()
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

async def set_input_quantity():
    log_wait("set_input_quantity")
    await civitai_page.locator("input#input_quantity").fill("4")
    log_done("set_input_quantity")

async def give_no_tips():
    log_wait("give_no_tips")
    await civitai_page.locator(generation_info_button_selector).click()
    await civitai_page.locator(creator_tip_selector).fill("0%")
    await civitai_page.locator(civitai_tip_selector).fill("0%")
    log_done("give_no_tips")

async def prepare_session(first_session_preparation: bool):
    await remove_cookies()
    if first_session_preparation:
        await skip_getting_started()
    await enter_generation_perspective()
    await confirm_start_generating_yellow_button()
    await claim_buzz()
    if first_session_preparation:
        await enter_parameters_perspective()
        await enable_mature_content()
    await enter_generation_perspective()
    await set_input_quantity()
    # await give_no_tips()

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
    seed = xml_root.find(".//seed").text if xml_root.find(".//seed") is not None else None
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

# periodical_generation: bool = True
# @app.post("/stop_generate_periodically")
# async def generate_periodically():
#     log_wait("generate_periodically")
#     global periodical_generation
#     periodical_generation = False

# @app.post("/start_generate_periodically")
# async def generate_periodically():
#     log_wait("generate_periodically")
#     global periodical_generation
#     periodical_generation = True
#     while periodical_generation:
#         await civitai_page.locator(generation_button_selector).click()
#         await asyncio.sleep(3)

@app.post("/generate_till_no_buzz")
async def generate_till_no_buzz():
    log_wait("generate_till_no_buzz")
    await give_no_tips()
    buzz_remain: bool = True
    while buzz_remain is True:
        job_available: bool = (await civitai_page.locator(generation_unavailable_selector).count()) == 0
        # buzz_remain: bool = (await civitai_page.locator(remaining_buzz_count_and_no_more_buzz_triangle_svg_selector).count()) == 1
        buzz_remain: bool = (await civitai_page.locator(no_more_buzz_triangle_svg_selector).count()) == 0
        print("job_available: " + str(job_available))
        print("buzz_remain: " + str(buzz_remain))
        if job_available and buzz_remain:
            await civitai_page.locator(generation_button_selector).click()
        await asyncio.sleep(3)
    log_done("generate_till_no_buzz")

async def inject(prompt: Prompt, injectSeed: bool):
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
    if prompt.seed is not None and injectSeed:
        await set_seed(prompt.seed)
    # await generate_till_no_buzz()

@app.post("/inject_prompt")
async def inject_prompt(file: UploadFile = File(...), injectSeed: bool = False):
    """Validates an uploaded XML file against an XSD schema from a given URL.

    Returns:
        A JSON response indicating whether the XML is valid or not.
    """
    try:
        # Read XML content
        xml_content = await file.read()
        xml_tree = ET.ElementTree(ET.fromstring(xml_content))
        root = xml_tree.getroot()
        
        prompt = parse_prompt(root)
        print(prompt.model_dump())
        await inject(prompt, injectSeed)

    except ET.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("civitaikido:app", host="127.0.0.1", port=8000, reload=True)
