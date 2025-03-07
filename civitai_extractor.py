#!./python

from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio

# adguard_mail_selector = '#app > main > div > section.address > div > div > div > button.address__copy > span.address__copy-text'
civitai_selectors = {
    'positivePromptArea': "#input_prompt",
    'negativePromptArea': "#input_negativePrompt",
    'cfgScaleHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div:nth-child(1) > div > div.mantine-Slider-root.flex-1.mantine-15k342w > input[type=hidden]",
    'cfgScaleTextInput': "#mantine-rh",
    'samplerHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div.mantine-InputWrapper-root.mantine-Select-root.mantine-1m3pqry > div > input[type=hidden]",
    'samplerSearchInput': "#input_sampler",
    'stepsHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div:nth-child(3) > div > div.mantine-Slider-root.flex-1.mantine-15k342w > input[type=hidden]",
    'stepsTextInput': "#mantine-rj"
}
civitai_generation_url = "https://civitai.com/generate"
# adguard_page_url = "https://adguard.com/fr/adguard-temp-mail/overview.html"

# Global variables
browser = None
civitai_page = None
adguard_page = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and close Playwright browser properly."""
    global browser, civitai_page, adguard_page

    # Start Playwright and browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        locale="en-US",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,  # Keep JS enabled
        ignore_https_errors=True,  # Bypass HTTPS issues
        timezone_id="America/New_York",  # Set a realistic timezone
        permissions=["geolocation"],  # Allow real geolocation
    )

    civitai_page = await context.new_page()

    # ✅ Fix: Define 'opts' before stealth
    await civitai_page.add_init_script("const opts = {};")
    await stealth_async(civitai_page)

    # ✅ Set auth headers (if required)
    await civitai_page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    })

    await civitai_page.goto(civitai_generation_url)

    # ✅ Fix: Wait for page load using a reliable selector
    try:
        await civitai_page.wait_for_selector("body", timeout=15000)
        print("✅ Page loaded successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Page may not have fully loaded: {e}")

    await civitai_page.wait_for_load_state("networkidle")  # Ensure everything loads
    await asyncio.sleep(3)  # Let JavaScript execute

    print("✅ Browser running with anti-bot protections")
    yield

    await browser.close()
    await playwright.stop()
    print("🛑 Browser closed!")

app = FastAPI(lifespan=lifespan)

@app.get(path="/extract-prompt")
async def extract_prompt():
    """Scrapes and returns text content from CivitAI using predefined selectors."""
    if not civitai_page:
        return {"error": "Browser not initialized"}

    prompt_scraps = {}

    for field, selector in civitai_selectors.items():
        try:
            element = await civitai_page.query_selector(selector)
            text = await element.inner_text() if element else "Not found"
            prompt_scraps[field] = text
        except Exception as e:
            prompt_scraps[field] = f"Error: {e}"

    return {"content": prompt_scraps}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("civitai_extractor:app", host="127.0.0.1", port=8000, reload=True)
