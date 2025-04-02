import asyncio

from src.config import GLOBAL_TIMEOUT
from src.service import BrowserManager
from src.util import try_action


class PopupRemover:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def remove_cookies(self):
        async def interact():
            await self.browser_manager.page.get_by_text("Customise choices").wait_for(state="visible", timeout=GLOBAL_TIMEOUT)
            await self.browser_manager.page.get_by_text("Customise choices").click()
            await self.browser_manager.page.get_by_text("Save preferences").click()
        await try_action("remove_cookies", interact)
    async def skip_getting_started(self):
        async def interact():
            await self.browser_manager.page.get_by_role("button", name="Skip").wait_for(state="visible", timeout=GLOBAL_TIMEOUT)
            await self.browser_manager.page.get_by_role("button", name="Skip").click()
        await try_action("skip_getting_started", interact)
    async def skip_getting_started_if_first_session_preparation(self, ask_first_session_preparation: bool):
        if ask_first_session_preparation:
            await self.skip_getting_started()

    async def remove_popups(self, ask_first_session_preparation: bool):
        await asyncio.gather(
            self.skip_getting_started_if_first_session_preparation(ask_first_session_preparation),
            self.remove_cookies()
        )
