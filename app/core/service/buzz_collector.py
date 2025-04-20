import asyncio

from core.constant import WAIT_PREFIX, DONE_PREFIX
from core.service import BrowserManager, ProfilePreparator
from core.util import try_action, like_all_pictures

import logging


logger = logging.getLogger(__name__)

class BuzzCollector:
    browser_manager: BrowserManager
    profile_preparator: ProfilePreparator
    def __init__(self, browser_manager: BrowserManager, profile_preparator: ProfilePreparator):
        self.browser_manager = browser_manager
        self.profile_preparator = profile_preparator
    async def prepare_and_like_pictures(self):
        await self.profile_preparator.prepare_profile()
        await like_all_pictures(self.browser_manager.page)
    async def collect_buzz_for_urls(self, urls: list[str]) -> None:
        logger.debug(WAIT_PREFIX + "collect_buzz_for_urls")
        for url in urls:
            if self.browser_manager.signed_in_civitai_generation_url != url:
                await self.browser_manager.init_page(url)
            await asyncio.gather(
                try_action("profile_preparator.prepare_profile", self.prepare_and_like_pictures)
            )
        logger.debug(DONE_PREFIX + "collect_buzz_for_urls")
