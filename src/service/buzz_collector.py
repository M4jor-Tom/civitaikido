from src.constant import WAIT_PREFIX, DONE_PREFIX
from src.service import BrowserManager, CivitaiPagePreparator
from src.util import try_action

import logging

from src.util.buzz_collection import like_all_pictures

logger = logging.getLogger(__name__)

class BuzzCollector:
    browser_manager: BrowserManager
    civitai_page_preparator: CivitaiPagePreparator
    def __init__(self, browser_manager: BrowserManager, civitai_page_preparator: CivitaiPagePreparator):
        self.browser_manager = browser_manager
        self.civitai_page_preparator = civitai_page_preparator
    async def collect_buzz_for_urls(self, urls: list[str]) -> None:
        logger.info(WAIT_PREFIX + "collect_buzz_for_urls")
        for url in urls:
            if self.browser_manager.signed_in_civitai_generation_url != url:
                await self.browser_manager.init_page(url)
            async def interact():
                await self.civitai_page_preparator.prepare_civitai_page(False)
                await like_all_pictures(self.browser_manager.page)
            await try_action("civitai_page_preparator.prepare_civitai_page", interact)
        logger.info(DONE_PREFIX + "collect_buzz_for_urls")
