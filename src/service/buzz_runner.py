from src.service import BrowserManager, CivitaiPagePreparator
from src.util import try_action


class BuzzRunner:
    browser_manager: BrowserManager
    civitai_page_preparator: CivitaiPagePreparator
    def __init__(self, browser_manager: BrowserManager, civitai_page_preparator: CivitaiPagePreparator):
        self.browser_manager = browser_manager
        self.civitai_page_preparator = civitai_page_preparator
    async def pick_all_buzz(self, urls: list[str]) -> None:
        for url in urls:
            await self.browser_manager.init_page(url)
            async def interact():
                await self.civitai_page_preparator.prepare_civitai_page(False)
            await try_action("civitai_page_preparator.prepare_civitai_page", interact)
