import logging

from playwright.async_api import Page

from core.config import INTERACTION_TIMEOUT
from core.constant import WAIT_PREFIX, DONE_PREFIX
from core.util import try_action, click_if_visible

logger = logging.getLogger(__name__)

async def remove_cookies(page: Page):
    async def interact():
        await page.get_by_text("Customise choices").wait_for(
            state="visible",
            timeout=INTERACTION_TIMEOUT)
        await page.get_by_text("Customise choices").click()
        await page.get_by_text("Save preferences").click()

    await try_action("remove_cookies", interact)

async def skip_getting_started(page: Page):
    async def interact():
        await page.get_by_role("button", name="Skip").wait_for(
            state="visible",
            timeout=INTERACTION_TIMEOUT)
        await page.get_by_role("button", name="Skip").click()

    await try_action("skip_getting_started", interact)

async def confirm_start_generating_yellow_button(page: Page):
    logger.debug(WAIT_PREFIX + "confirm_start_generating_yellow_button")
    await click_if_visible("confirm_start_generating_yellow_button",
                           page.get_by_role("button", name="I Confirm, Start Generating"))
    logger.debug(DONE_PREFIX + "confirm_start_generating_yellow_button")
