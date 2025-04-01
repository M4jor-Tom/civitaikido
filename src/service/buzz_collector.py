from src.constant import like_image_button_selector, feed_perspective_button_selector, WAIT_PREFIX, DONE_PREFIX
from src.service import BrowserManager, CivitaiPagePreparator
from src.util import try_action

import logging

logger = logging.getLogger(__name__)

class BuzzCollector:
    browser_manager: BrowserManager
    civitai_page_preparator: CivitaiPagePreparator
    def __init__(self, browser_manager: BrowserManager, civitai_page_preparator: CivitaiPagePreparator):
        self.browser_manager = browser_manager
        self.civitai_page_preparator = civitai_page_preparator
    async def enter_feed_view(self):
        logger.info(WAIT_PREFIX + "enter_feed_view")
        await self.browser_manager.page.locator(feed_perspective_button_selector).first.click()
        logger.info(DONE_PREFIX + "enter_feed_view")
    async def like_all_pictures(self) -> None:
        logger.info(WAIT_PREFIX + "like_all_pictures")
        await self.enter_feed_view()
        like_image_buttons = await self.browser_manager.page.locator(like_image_button_selector).all()
        for like_image_button in like_image_buttons:
            await like_image_button.click()
        logger.info(DONE_PREFIX + "like_all_pictures")
    async def collect_buzz_for_urls(self, urls: list[str]) -> None:
        logger.info(WAIT_PREFIX + "collect_buzz_for_urls")
        for url in urls:
            if self.browser_manager.signed_in_civitai_generation_url != url:
                await self.browser_manager.init_page(url)
            async def interact():
                await self.civitai_page_preparator.prepare_civitai_page(False)
                await self.like_all_pictures()
            await try_action("civitai_page_preparator.prepare_civitai_page", interact)
        logger.info(DONE_PREFIX + "collect_buzz_for_urls")
