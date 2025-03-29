import logging
from src.config import global_timeout
from src.util import try_action, click_if_visible, WAIT_PREFIX, DONE_PREFIX

logger = logging.getLogger(__name__)

class PrepareCivitaiPage:
    page: any

    def __init__(self, page):
        self.page = page

    async def remove_cookies(self):
        async def interact():
            await self.page.get_by_text("Customise choices").wait_for(state="visible", timeout=global_timeout)
            await self.page.get_by_text("Customise choices").click()
            await self.page.get_by_text("Save preferences").click()

        await try_action("remove_cookies", interact)

    async def enter_parameters_perspective(self):
        async def interact():
            await self.page.locator('div[title]').first.click()
            await self.page.locator('a[href="/user/account"]').first.click()

        await try_action("enter_parameters_perspective", interact)

    async def enable_mature_content(self):
        async def interact():
            await self.page.locator('//*[text()="Show mature content"]').first.click()
            await self.page.locator('//*[text()="Blur mature content"]').first.click()
            # await self.page.locator('//*[text()="PG"]').first.click()
            # await self.page.locator('//*[text()="Safe for work. No naughty stuff"]').first.click()
            # await self.page.locator('//*[text()="PG-13"]').first.click()
            await self.page.locator('//*[text()="Revealing clothing, violence, or light gore"]').first.click()
            # await self.page.locator('//*[text()="R"]').first.click()
            await self.page.locator(
                '//*[text()="Adult themes and situations, partial nudity, graphic violence, or death"]').first.click()
            # await self.page.locator('//*[text()="X"]').first.click()
            await self.page.locator('//*[text()="Graphic nudity, adult objects, or settings"]').first.click()
            # await self.page.locator('//*[text()="XXX"]').first.click()
            await self.page.locator('//*[text()="Overtly sexual or disturbing graphic content"]').first.click()

        await try_action("enable_mature_content", interact)

    async def enter_generation_perspective(self):
        async def interact():
            await self.page.locator('button[data-activity="create:navbar"]').first.click()
            await self.page.locator('a[href="/generate"]').first.click()

        await try_action("enter_generation_perspective", interact)
        # await self.page.goto(civitai_generation_url)

    async def skip_getting_started(self):
        async def interact():
            await self.page.get_by_role("button", name="Skip").wait_for(state="visible", timeout=global_timeout)
            await self.page.get_by_role("button", name="Skip").click()

        await try_action("skip_getting_started", interact)

    async def confirm_start_generating_yellow_button(self):
        await click_if_visible("confirm_start_generating_yellow_button",
                               self.page.get_by_role("button", name="I Confirm, Start Generating"))

    async def claim_buzz(self):
        await click_if_visible("claim_buzz", self.page.locator('button:has-text("Claim 25 Buzz")'))

    async def set_input_quantity(self):
        logger.info(WAIT_PREFIX + "set_input_quantity")
        await self.page.locator("input#input_quantity").fill("4")
        logger.info(DONE_PREFIX + "set_input_quantity")

    async def prepare_session(self, ask_first_session_preparation: bool):
        await self.remove_cookies()
        if ask_first_session_preparation:
            await self.skip_getting_started()
        await self.enter_generation_perspective()
        await self.confirm_start_generating_yellow_button()
        await self.claim_buzz()
        if ask_first_session_preparation:
            await self.enter_parameters_perspective()
            await self.enable_mature_content()
        await self.enter_generation_perspective()
        await self.set_input_quantity()