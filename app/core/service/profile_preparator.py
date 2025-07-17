import asyncio
import logging
from core.constant import profile_icon_selector, profile_settings_button_selector, \
    show_mature_content_selector, blur_mature_content_selector, pg_13_content_selector, r_content_selector, \
    x_content_selector, xxx_content_selector, parameters_url, WAIT_PREFIX, DONE_PREFIX
from .browser_manager import BrowserManager
from core.util import try_action

logger = logging.getLogger(__name__)

class ProfilePreparator:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def enter_parameters_perspective_by_url(self):
        logger.debug(WAIT_PREFIX + "enter_parameters_perspective_by_url")
        await self.browser_manager.init_page(parameters_url)
        logger.debug(DONE_PREFIX + "enter_parameters_perspective_by_url")

    async def enter_parameters_perspective_by_buttons(self):
        logger.debug(WAIT_PREFIX + "enter_parameters_perspective_by_buttons")
        if await self.browser_manager.page.locator(profile_icon_selector).first.is_visible():
            await self.browser_manager.page.locator(profile_icon_selector).first.click()
        if await self.browser_manager.page.locator(profile_settings_button_selector).first.is_visible():
            await self.browser_manager.page.locator(profile_settings_button_selector).first.click()
        logger.debug(DONE_PREFIX + "enter_parameters_perspective_by_buttons")

    async def enable_mature_content(self):
        async def interact():
            await self.browser_manager.page.locator(show_mature_content_selector).first.click()
            await self.browser_manager.page.locator(blur_mature_content_selector).first.click()
            await self.browser_manager.page.locator(pg_13_content_selector).first.click()
            await self.browser_manager.page.locator(r_content_selector).first.click()
            await self.browser_manager.page.locator(x_content_selector).first.click()
            await self.browser_manager.page.locator(xxx_content_selector).first.click()
        await try_action("enable_mature_content", interact)

    async def prepare_profile(self):
        logger.debug(WAIT_PREFIX + "prepare_profile")
        await self.enter_parameters_perspective_by_buttons()
        await self.enable_mature_content()
        await self.browser_manager.enter_generation_perspective()
        await asyncio.sleep(3)
        logger.debug(DONE_PREFIX + "prepare_profile")
