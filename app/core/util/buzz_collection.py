import logging

from core.constant import WAIT_PREFIX, like_image_button_selector, DONE_PREFIX
from core.util import enter_feed_view

logger = logging.getLogger(__name__)

async def like_all_pictures(page: any) -> None:
    logger.debug(WAIT_PREFIX + "like_all_pictures")
    await enter_feed_view(page)
    like_image_buttons = await page.locator(like_image_button_selector).all()
    for like_image_button in like_image_buttons:
        await like_image_button.click()
    logger.debug(DONE_PREFIX + "like_all_pictures")
