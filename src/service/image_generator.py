from src.constant import generation_info_button_selector, creator_tip_selector, civitai_tip_selector, \
    no_more_buzz_triangle_svg_selector, \
    generation_button_selector, all_jobs_done_selector, WAIT_PREFIX, DONE_PREFIX
import logging
import asyncio

from . import BuzzCollector
from .browser_manager import BrowserManager
from ..config import GLOBAL_TIMEOUT

logger = logging.getLogger(__name__)

class ImageGenerator:
    browser_manager: BrowserManager
    buzz_collector: BuzzCollector

    def __init__(self, browser_manager: BrowserManager, buzz_collector: BuzzCollector):
        self.browser_manager = browser_manager
        self.buzz_collector = buzz_collector

    async def give_no_tips(self):
        logger.info(WAIT_PREFIX + "give_no_tips")
        await self.browser_manager.page.locator(generation_info_button_selector).click()
        await self.browser_manager.page.locator(creator_tip_selector).fill("0%")
        await self.browser_manager.page.locator(civitai_tip_selector).fill("0%")
        logger.info(DONE_PREFIX + "give_no_tips")

    async def generate_all_possible(self) -> None:
        logger.info(WAIT_PREFIX + "generate_all_possible")
        await self.generate_till_no_buzz()
        await self.buzz_collector.like_all_pictures()
        await self.generate_till_no_buzz()
        logger.info(DONE_PREFIX + "generate_all_possible")

    async def generate_till_no_buzz(self):
        logger.info(WAIT_PREFIX + "generate_till_no_buzz")
        logger.info(WAIT_PREFIX + "launch_all_generations")
        await self.give_no_tips()
        buzz_remain: bool = True
        while buzz_remain is True:
            buzz_remain: bool = (await self.browser_manager.page.locator(no_more_buzz_triangle_svg_selector).count()) == 0
            logger.info("buzz_remain: " + str(buzz_remain))
            if buzz_remain:
                await self.browser_manager.page.locator(generation_button_selector).wait_for(timeout=GLOBAL_TIMEOUT)
                await self.browser_manager.page.locator(generation_button_selector).click()
                await asyncio.sleep(3)
        logger.info(DONE_PREFIX + "launch_all_generations")
        await self.browser_manager.page.locator(all_jobs_done_selector).wait_for(timeout=GLOBAL_TIMEOUT)
        logger.info(DONE_PREFIX + "generate_till_no_buzz")