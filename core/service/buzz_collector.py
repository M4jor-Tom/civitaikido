import asyncio

from core.constant import WAIT_PREFIX, DONE_PREFIX
from core.service import BrowserManager, CivitaiPagePreparator, PopupRemover
from core.util import try_action

import logging

from core.util.buzz_collection import like_all_pictures

logger = logging.getLogger(__name__)

class BuzzCollector:
    browser_manager: BrowserManager
    civitai_page_preparator: CivitaiPagePreparator
    popup_remover: PopupRemover
    def __init__(self, browser_manager: BrowserManager, civitai_page_preparator: CivitaiPagePreparator, popup_remover: PopupRemover):
        self.browser_manager = browser_manager
        self.civitai_page_preparator = civitai_page_preparator
        self.popup_remover = popup_remover
    async def prepare_and_like_pictures(self):
        await self.civitai_page_preparator.prepare_civitai_page(False)
        await like_all_pictures(self.browser_manager.page)
    async def collect_buzz_for_urls(self, urls: list[str]) -> None:
        logger.info(WAIT_PREFIX + "collect_buzz_for_urls")
        for url in urls:
            if self.browser_manager.signed_in_civitai_generation_url != url:
                await self.browser_manager.init_page(url)
            await asyncio.gather(
                self.popup_remover.remove_popups(True),
                try_action("civitai_page_preparator.prepare_civitai_page", self.prepare_and_like_pictures)
            )
        logger.info(DONE_PREFIX + "collect_buzz_for_urls")
