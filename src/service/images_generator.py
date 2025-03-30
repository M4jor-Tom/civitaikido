from src.constant import generation_info_button_selector, creator_tip_selector, civitai_tip_selector, \
    no_more_buzz_triangle_svg_selector, \
    generation_button_selector, all_jobs_done_selector, WAIT_PREFIX, DONE_PREFIX, global_timeout
import logging
import asyncio

from .browser_manager import BrowserManager

logger = logging.getLogger(__name__)

class ImagesGenerator:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def give_no_tips(self):
        logger.info(WAIT_PREFIX + "give_no_tips")
        await self.browser_manager.page.locator(generation_info_button_selector).click()
        await self.browser_manager.page.locator(creator_tip_selector).fill("0%")
        await self.browser_manager.page.locator(civitai_tip_selector).fill("0%")
        logger.info(DONE_PREFIX + "give_no_tips")

    async def generate_till_no_buzz(self):
        logger.info(WAIT_PREFIX + "generate_till_no_buzz")
        logger.info(WAIT_PREFIX + "launch_all_generations")
        await self.give_no_tips()
        buzz_remain: bool = True
        while buzz_remain is True:
            buzz_remain: bool = (await self.browser_manager.page.locator(no_more_buzz_triangle_svg_selector).count()) == 0
            logger.info("buzz_remain: " + str(buzz_remain))
            if buzz_remain:
                await self.browser_manager.page.locator(generation_button_selector).wait_for(timeout=global_timeout)
                await self.browser_manager.page.locator(generation_button_selector).click()
                await asyncio.sleep(3)
        logger.info(DONE_PREFIX + "launch_all_generations")
        await self.browser_manager.page.locator(all_jobs_done_selector).wait_for(timeout=global_timeout)
        logger.info(DONE_PREFIX + "generate_till_no_buzz")