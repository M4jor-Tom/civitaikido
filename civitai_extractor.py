#!./python

from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from contextlib import asynccontextmanager
import asyncio

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

civitai_generation_url: str = "https://civitai.com/generate"
# adguard_mails_page_url: str = "https://adguard.com/fr/adguard-temp-mail/overview.html"

# Global variables
browser = None
civitai_page = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and close Playwright browser properly."""
    global browser, civitai_page

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

    # ✅ Ensure opts is defined to prevent ReferenceError
    await civitai_page.add_init_script("window.opts = {};")

    # ✅ Set auth headers (if required)
    await civitai_page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    })

    await civitai_page.goto(civitai_generation_url)

    # ✅ Ensure React fully loads before injecting scripts
    await civitai_page.wait_for_selector("#__next", timeout=15000)  # Wait for Next.js root

    try:
        await civitai_page.wait_for_load_state("domcontentloaded", timeout=15000)  # Avoids networkidle timeout
    except Exception:
        print("⚠️ Warning: Page load state took too long, continuing anyway.")

    await asyncio.sleep(5)  # Ensure JavaScript finishes executing

    # ✅ Apply stealth AFTER page has fully loaded
    await stealth_async(civitai_page)

    print("✅ Browser running with anti-bot protections")
    yield

    await browser.close()
    await playwright.stop()
    print("🛑 Browser closed!")

app = FastAPI(lifespan=lifespan)

@app.get("/extract-prompt")
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
