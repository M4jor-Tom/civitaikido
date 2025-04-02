from src.constant import feed_perspective_button_selector, WAIT_PREFIX, DONE_PREFIX

import logging

logger = logging.getLogger(__name__)

async def enter_feed_view(page: any):
    logger.info(WAIT_PREFIX + "enter_feed_view")
    await page.locator(feed_perspective_button_selector).first.click()
    logger.info(DONE_PREFIX + "enter_feed_view")
