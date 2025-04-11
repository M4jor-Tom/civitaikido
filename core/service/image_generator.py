from core.constant import generation_info_button_selector, creator_tip_selector, civitai_tip_selector, \
    no_more_buzz_triangle_svg_selector, \
    generation_button_selector, all_jobs_done_selector, WAIT_PREFIX, DONE_PREFIX, claim_buzz_button_selector, \
    generation_quantity_input_selector
import logging
import asyncio

from .browser_manager import BrowserManager
from ..config import INTERACTION_TIMEOUT
from ..util import click_if_visible
from ..util.buzz_collection import like_all_pictures
from ..util.page_preparation import confirm_start_generating_yellow_button

logger = logging.getLogger(__name__)

class ImageGenerator:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def give_no_tips(self):
        logger.debug(WAIT_PREFIX + "give_no_tips")
        await self.browser_manager.page.locator(generation_info_button_selector).click()
        await self.browser_manager.page.locator(creator_tip_selector).fill("0%")
        await self.browser_manager.page.locator(civitai_tip_selector).fill("0%")
        logger.debug(DONE_PREFIX + "give_no_tips")

    async def launch_all_possible_generations(self) -> None:
        logger.debug(WAIT_PREFIX + "generate_all_possible")
        await self.launch_generations_batch()
        await self.browser_manager.page.locator(all_jobs_done_selector).wait_for(timeout=INTERACTION_TIMEOUT)
        await like_all_pictures(self.browser_manager.page)
        await self.launch_generations_batch()
        logger.debug(DONE_PREFIX + "generate_all_possible")

    async def claim_buzz(self):
        logger.debug(WAIT_PREFIX + "claim_buzz")
        await click_if_visible("claim_buzz", self.browser_manager.page.locator(claim_buzz_button_selector))
        logger.debug(DONE_PREFIX + "claim_buzz")

    async def set_input_quantity(self):
        logger.debug(WAIT_PREFIX + "set_input_quantity")
        await self.browser_manager.page.locator(generation_quantity_input_selector).fill("4")
        logger.debug(DONE_PREFIX + "set_input_quantity")

    async def launch_generations_batch(self):
        logger.debug(WAIT_PREFIX + "launch_all_generations")
        await confirm_start_generating_yellow_button(self.browser_manager.page)
        await self.claim_buzz()
        await self.set_input_quantity()
        await self.give_no_tips()
        buzz_remain: bool = True
        while buzz_remain is True:
            buzz_remain: bool = (await self.browser_manager.page.locator(no_more_buzz_triangle_svg_selector).count()) == 0
            logger.debug("buzz_remain: " + str(buzz_remain))
            if buzz_remain:
                await self.browser_manager.page.locator(generation_button_selector).wait_for(timeout=INTERACTION_TIMEOUT)
                await self.browser_manager.page.locator(generation_button_selector).click()
                await asyncio.sleep(3)
        logger.debug(DONE_PREFIX + "launch_generations_batch")
