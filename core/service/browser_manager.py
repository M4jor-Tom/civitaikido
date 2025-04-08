from asyncio import Task

from fastapi import HTTPException
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError
from playwright_stealth.stealth import stealth_async
import asyncio
import logging

from core.config import INTERACTION_TIMEOUT, HEADLESS
from core.constant import *
from core.model.injection_extraction_state import InjectionExtractionState
from core.service import StateManager
from core.util import try_action, remove_cookies, skip_getting_started

logger = logging.getLogger(__name__)

class BrowserManager:
    state_manager: StateManager
    browser: Browser | None
    context: BrowserContext | None
    page: Page | None
    signed_in_civitai_generation_url: str | None

    def __init__(self, state_manager: StateManager):
        self.browser = None
        self.context = None
        self.page = None
        self.signed_in_civitai_generation_url = None
        self.state_manager = state_manager
        self.page_tasks: list[Task] = []

    async def init_browser(self):
        """Initializes the browser when the URL is set."""
        logger.info(WAIT_PREFIX + "Browser to initialise...")

        # Wait until a URL is set
        while self.signed_in_civitai_generation_url is None:
            logger.debug("Poll for signed_in_civitai_generation_url to have a value...")
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
        self.context.set_default_timeout(INTERACTION_TIMEOUT)
        await self.init_page(str(self.signed_in_civitai_generation_url))
        self.state_manager.update_injection_extraction_state(InjectionExtractionState.BROWSER_OPEN)

    async def close_page(self) -> None:
        canceled_count: int = 0
        for task in self.page_tasks:
            if task.cancel():
                canceled_count += 1
        self.page_tasks.clear()
        logger.debug(f"close_page: killed {canceled_count} tasks")
        await self.page.close()

    async def init_page(self, new_page_url: str) -> None:
        new_page: Page = await self.context.new_page()
        self.page_tasks.append(asyncio.create_task(remove_cookies(new_page)))
        self.page_tasks.append(asyncio.create_task(skip_getting_started(new_page)))
        if self.page:
            await self.close_page()
        self.page = new_page
        # await self.page.add_init_script(
        #    """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
        #)
        # Load the provided URL
        await self.page.goto(new_page_url)
        await self.page.wait_for_selector("#__next", timeout=INTERACTION_TIMEOUT)

        try:
            await self.page.wait_for_load_state("domcontentloaded", timeout=INTERACTION_TIMEOUT)
        except TimeoutError:
            logger.warning(SKIP_PREFIX + "Page load state took too long, continuing anyway.")

        await asyncio.sleep(5)

        # Apply stealth mode
        await stealth_async(self.page)

    async def shutdown_if_possible(self) -> None:
        if self.page:
            await self.close_page()
            logger.info("🛑 Page closed!")
            self.page = None
        if self.context:
            await self.context.close()
            logger.info("🛑 Context closed!")
            self.context = None
        if self.browser:
            await self.browser.close()
            logger.info("🛑 Browser closed!")
            self.browser = None

    async def open_browser(self, civitai_connection_url: str):
        """Sets the signed-in CivitAI generation URL and unblocks the browser startup."""
        if not civitai_connection_url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        self.signed_in_civitai_generation_url = civitai_connection_url
        logger.info(WAIT_PREFIX + "message: URL set successfully; Session prepared for xml injection, url: " + self.signed_in_civitai_generation_url)
        while self.state_manager.injection_extraction_state != InjectionExtractionState.BROWSER_OPEN:
            await asyncio.sleep(1)

    async def enter_generation_perspective(self):
        await self.enter_generation_perspective_by_buttons()

    async def enter_generation_perspective_by_url(self):
        await self.init_page(generation_perspective_url)

    async def enter_generation_perspective_by_buttons(self):
        async def interact():
            await self.page.locator(create_prompt_header_button_selector).first.click()
            await self.page.locator(generate_dropdown_option_selector).first.click()
        await try_action("enter_generation_perspective", interact)