#!./python

from fastapi import FastAPI
from playwright.sync_api import sync_playwright

adguard_mail_selector: str = '#app > main > div > section.address > div > div > div > button.address__copy > span.address__copy-text'
civitai_selectors: dict[str, str] = {
    'positivePromptArea': "#input_prompt",
    'negativePromptArea': "#input_negativePrompt",
    'cfgScaleHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div:nth-child(1) > div > div.mantine-Slider-root.flex-1.mantine-15k342w > input[type=hidden]",
    'cfgScaleTextInput': "#mantine-rh",
    'samplerHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div.mantine-InputWrapper-root.mantine-Select-root.mantine-1m3pqry > div > input[type=hidden]",
    'samplerSearchInput': "#input_sampler",
    'stepsHiddenInput': "#mantine-rf-panel-advanced > div > div > div > div.relative.flex.flex-col.gap-3 > div:nth-child(3) > div > div.mantine-Slider-root.flex-1.mantine-15k342w > input[type=hidden]",
    'stepsTextInput': "#mantine-rj"
};
civitai_generation_url: str = "https://civitai.com/generate"
adguard_page_url: str = "https://adguard.com/fr/adguard-temp-mail/overview.html"

app = FastAPI()

def launch_browser():
    global browser, civitai_page, adguard_page
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    civitai_page = browser.new_page()
    adguard_page = browser.new_page()
    civitai_page.goto(civitai_generation_url)
    adguard_page.goto(adguard_page_url)

@app.get("/extract-mail")
def extract_content():
    text = adguard_page.evaluate("document.body.innerText")
    return {"content": text[:500]}

@app.get("/extract-prompt")
def extract_content():
    prompt_scraps: dict[str, str] = {}
    for field, civitai_seelector in civitai_selectors:
        element = civitai_page.query_selector(civitai_seelector)
        prompt_scraps[field] = element
    return {"content": prompt_scraps}

if __name__ == "__main__":
    import uvicorn
    launch_browser()
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
