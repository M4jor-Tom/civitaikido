from core.constant import feed_perspective_button_selector, WAIT_PREFIX, DONE_PREFIX

from playwright.async_api import Page


import logging

logger = logging.getLogger(__name__)

async def enter_feed_view(page: Page):
    logger.debug(WAIT_PREFIX + "enter_feed_view")
    await page.locator(feed_perspective_button_selector).first.click()
    logger.debug(DONE_PREFIX + "enter_feed_view")

