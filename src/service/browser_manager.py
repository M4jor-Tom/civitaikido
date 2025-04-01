from fastapi import HTTPException
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
import asyncio
import logging

from src.config import GLOBAL_TIMEOUT, HEADLESS
from src.constant import *

logger = logging.getLogger(__name__)

class BrowserManager:
    browser: any
    context: any
    page: any
    signed_in_civitai_generation_url: str | None
    browser_initialized: bool

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.signed_in_civitai_generation_url = None
        self.browser_initialized = False

    async def init_browser(self):
        """Initializes the browser when the URL is set."""
        logger.info(WAIT_PREFIX + "Browser to initialise...")

        # Wait until a URL is set
        while self.signed_in_civitai_generation_url is None:
            await asyncio.sleep(1)

        logger.info(DONE_PREFIX + "URL received: " + str(self.signed_in_civitai_generation_url))

        # Start Playwright
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=HEADLESS)

        self.context = await self.browser.new_context(
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
        self.context.set_default_timeout(GLOBAL_TIMEOUT)
        await self.init_page(str(self.signed_in_civitai_generation_url))
        self.browser_initialized = True

    async def init_page(self, url: str) -> None:
        self.page = await self.context.new_page()

        # Load the provided URL
        await self.page.goto(url)

        await self.page.wait_for_selector("#__next", timeout=GLOBAL_TIMEOUT)

        try:
            await self.page.wait_for_load_state("domcontentloaded", timeout=GLOBAL_TIMEOUT)
        except Exception:
            logger.warning(SKIP_PREFIX + "Page load state took too long, continuing anyway.")

        await asyncio.sleep(5)

        # Apply stealth mode
        await stealth_async(self.page)

    async def shutdown_if_possible(self) -> None:
        # Shutdown sequence
        if self.browser:
            await self.page.close()
            await self.browser.close()
            logger.info("🛑 Browser closed!")

    async def open_browser(self, civitai_connection_url: str):
        """Sets the signed-in CivitAI generation URL and unblocks the browser startup."""
        if not civitai_connection_url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        self.signed_in_civitai_generation_url = civitai_connection_url
        logger.info(WAIT_PREFIX + "message: URL set successfully; Session prepared for xml injection, url: " + self.signed_in_civitai_generation_url)
        while not self.browser_initialized:
            await asyncio.sleep(1)
