#!./python

from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import stealth
from contextlib import asynccontextmanager

adguard_mail_selector = '#app > main > div > section.address > div > div > div > button.address__copy > span.address__copy-text'
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
adguard_page_url = "https://adguard.com/fr/adguard-temp-mail/overview.html"

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
    )

    civitai_page = await context.new_page()
    adguard_page = await context.new_page()

    await stealth(civitai_page)
    await stealth(adguard_page)

    await civitai_page.goto(civitai_generation_url)
    await adguard_page.goto(adguard_page_url)

    print("✅ Browser running with anti-bot protections")
    yield

    await browser.close()
    await playwright.stop()
    print("🛑 Browser closed!")

app = FastAPI(lifespan=lifespan)

@app.get("/extract-mail")
async def extract_content():
    """Extracts text from the AdGuard page."""
    if not adguard_page:
        return {"error": "Browser not initialized"}
    text = await adguard_page.evaluate("document.body.innerText")
    return {"content": text[:500]}

@app.get("/extract-prompt")
async def extract_prompt():
    """Extracts prompt fields from the CivitAI page."""
    if not civitai_page:
        return {"error": "Browser not initialized"}
    
    prompt_scraps = {}
    for field, selector in civitai_selectors.items():
        element = await civitai_page.query_selector(selector)
        prompt_scraps[field] = await element.inner_text() if element else "Not found"
    
    return {"content": prompt_scraps}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("civitai_extractor:app", host="127.0.0.1", port=8000, reload=True)
