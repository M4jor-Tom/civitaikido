from core.constant import feed_perspective_button_selector, WAIT_PREFIX, DONE_PREFIX, \
    create_prompt_header_button_selector, generate_dropdown_option_selector
from playwright.async_api import Page


import logging

from core.util import try_action

logger = logging.getLogger(__name__)

async def enter_feed_view(page: Page):
    logger.info(WAIT_PREFIX + "enter_feed_view")
    await page.locator(feed_perspective_button_selector).first.click()
    logger.info(DONE_PREFIX + "enter_feed_view")

async def enter_generation_perspective(page: Page):
    async def interact():
        await page.locator(create_prompt_header_button_selector).first.click()
        await page.locator(generate_dropdown_option_selector).first.click()
    await try_action("enter_generation_perspective", interact)
