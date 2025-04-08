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

logger = logging.getLogger(__name__)

class ImageGenerator:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def give_no_tips(self):
        logger.info(WAIT_PREFIX + "give_no_tips")
        await self.browser_manager.page.locator(generation_info_button_selector).click()
        await self.browser_manager.page.locator(creator_tip_selector).fill("0%")
        await self.browser_manager.page.locator(civitai_tip_selector).fill("0%")
        logger.info(DONE_PREFIX + "give_no_tips")

    async def generate_all_possible(self) -> None:
        logger.info(WAIT_PREFIX + "generate_all_possible")
        await self.generate_till_no_buzz()
        await like_all_pictures(self.browser_manager.page)
        await self.generate_till_no_buzz()
        logger.info(DONE_PREFIX + "generate_all_possible")

    async def confirm_start_generating_yellow_button(self):
        logger.info(WAIT_PREFIX + "confirm_start_generating_yellow_button")
        await click_if_visible("confirm_start_generating_yellow_button",
                               self.browser_manager.page.get_by_role("button", name="I Confirm, Start Generating"))
        logger.info(DONE_PREFIX + "confirm_start_generating_yellow_button")

    async def claim_buzz(self):
        logger.info(WAIT_PREFIX + "claim_buzz")
        await click_if_visible("claim_buzz", self.browser_manager.page.locator(claim_buzz_button_selector))
        logger.info(DONE_PREFIX + "claim_buzz")

    async def set_input_quantity(self):
        logger.debug(WAIT_PREFIX + "set_input_quantity")
        await self.browser_manager.page.locator(generation_quantity_input_selector).fill("4")
        logger.debug(DONE_PREFIX + "set_input_quantity")

    async def generate_till_no_buzz(self):
        logger.info(WAIT_PREFIX + "generate_till_no_buzz")
        logger.info(WAIT_PREFIX + "launch_all_generations")
        await self.confirm_start_generating_yellow_button()
        await self.claim_buzz()
        await self.set_input_quantity()
        await self.give_no_tips()
        buzz_remain: bool = True
        while buzz_remain is True:
            buzz_remain: bool = (await self.browser_manager.page.locator(no_more_buzz_triangle_svg_selector).count()) == 0
            logger.info("buzz_remain: " + str(buzz_remain))
            if buzz_remain:
                await self.browser_manager.page.locator(generation_button_selector).wait_for(timeout=INTERACTION_TIMEOUT)
                await self.browser_manager.page.locator(generation_button_selector).click()
                await asyncio.sleep(3)
        logger.info(DONE_PREFIX + "launch_all_generations")
        await self.browser_manager.page.locator(all_jobs_done_selector).wait_for(timeout=INTERACTION_TIMEOUT)
        logger.info(DONE_PREFIX + "generate_till_no_buzz")
