import logging
from src.constant import profile_icon_selector, profile_settings_button_selector, \
    show_mature_content_selector, blur_mature_content_selector, pg_13_content_selector, r_content_selector, \
    x_content_selector, xxx_content_selector, create_prompt_header_button_selector, generate_dropdown_option_selector, \
    claim_buzz_button_selector, generation_quantity_input_selector, WAIT_PREFIX, DONE_PREFIX
from .browser_manager import BrowserManager
from src.util import try_action, click_if_visible
from ..config import GLOBAL_TIMEOUT

logger = logging.getLogger(__name__)

class CivitaiPagePreparator:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def remove_cookies(self):
        async def interact():
            await self.browser_manager.page.get_by_text("Customise choices").wait_for(state="visible", timeout=GLOBAL_TIMEOUT)
            await self.browser_manager.page.get_by_text("Customise choices").click()
            await self.browser_manager.page.get_by_text("Save preferences").click()

        await try_action("remove_cookies", interact)

    async def enter_parameters_perspective(self):
        async def interact():
            await self.browser_manager.page.locator(profile_icon_selector).first.click()
            await self.browser_manager.page.locator(profile_settings_button_selector).first.click()

        await try_action("enter_parameters_perspective", interact)

    async def enable_mature_content(self):
        async def interact():
            await self.browser_manager.page.locator(show_mature_content_selector).first.click()
            await self.browser_manager.page.locator(blur_mature_content_selector).first.click()
            await self.browser_manager.page.locator(pg_13_content_selector).first.click()
            await self.browser_manager.page.locator(r_content_selector).first.click()
            await self.browser_manager.page.locator(x_content_selector).first.click()
            await self.browser_manager.page.locator(xxx_content_selector).first.click()

        await try_action("enable_mature_content", interact)

    async def enter_generation_perspective(self):
        async def interact():
            await self.browser_manager.page.locator(create_prompt_header_button_selector).first.click()
            await self.browser_manager.page.locator(generate_dropdown_option_selector).first.click()
        await try_action("enter_generation_perspective", interact)

    async def skip_getting_started(self):
        async def interact():
            await self.browser_manager.page.get_by_role("button", name="Skip").wait_for(state="visible", timeout=GLOBAL_TIMEOUT)
            await self.browser_manager.page.get_by_role("button", name="Skip").click()

        await try_action("skip_getting_started", interact)

    async def confirm_start_generating_yellow_button(self):
        await click_if_visible("confirm_start_generating_yellow_button",
                               self.browser_manager.page.get_by_role("button", name="I Confirm, Start Generating"))

    async def claim_buzz(self):
        await click_if_visible("claim_buzz", self.browser_manager.page.locator(claim_buzz_button_selector))

    async def set_input_quantity(self):
        logger.info(WAIT_PREFIX + "set_input_quantity")
        await self.browser_manager.page.locator(generation_quantity_input_selector).fill("4")
        logger.info(DONE_PREFIX + "set_input_quantity")

    async def prepare_civitai_page(self, ask_first_session_preparation: bool):
        await self.remove_cookies()
        if ask_first_session_preparation:
            await self.skip_getting_started()
        await self.enter_generation_perspective()
        await self.confirm_start_generating_yellow_button()
        await self.claim_buzz()
        if ask_first_session_preparation:
            await self.enter_parameters_perspective()
            await self.enable_mature_content()
        await self.enter_generation_perspective()
        await self.set_input_quantity()