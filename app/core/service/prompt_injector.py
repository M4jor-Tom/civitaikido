from core.constant import model_search_input_selector, WAIT_PREFIX, DONE_PREFIX, resource_option_selector, \
    lora_weight_selector, create_with_resource_selector, additional_resource_accordion_selector, \
    cfg_scale_input_selector, sampler_input_selector, sampler_option_selector_prefix, sampler_option_selector_suffix, \
    steps_input_selector
from core.model import Prompt, Resource
from .browser_manager import BrowserManager
import logging
import asyncio

from core.util import try_action
from ..config import INTERACTION_TIMEOUT

logger = logging.getLogger(__name__)

class PromptInjector:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def add_resource(self, resource: Resource):
        if resource.page_url:
            await self.add_resource_by_page_url(page_url=resource.page_url)
        else:
            await self.add_resource_by_hash(resource_hash=resource.hash)

    async def add_resource_by_page_url(self, page_url: str):
        logger.debug(WAIT_PREFIX + "add_resource_by_page_url: " + page_url)
        await self.browser_manager.init_page(page_url)
        await self.browser_manager.page.locator(create_with_resource_selector).wait_for(timeout=INTERACTION_TIMEOUT)
        await self.browser_manager.page.locator(create_with_resource_selector).click()
        await self.browser_manager.enter_generation_perspective()
        logger.debug(DONE_PREFIX + "add_resource_by_page_url: " + page_url)

    async def add_resource_by_hash(self, resource_hash: str):
        logger.debug(WAIT_PREFIX + "add_resource_by_hash: " + resource_hash)
        await self.browser_manager.page.locator(model_search_input_selector).fill(resource_hash)
        await self.browser_manager.page.locator(resource_option_selector).first.click(force=True)
        await self.browser_manager.page.locator(create_with_resource_selector).wait_for(timeout=INTERACTION_TIMEOUT)
        await self.browser_manager.page.locator(create_with_resource_selector).click()
        await self.browser_manager.enter_generation_perspective()
        logger.debug(DONE_PREFIX + "add_resource_by_hash: " + resource_hash)

    async def open_additional_resources_accordion(self):
        logger.debug(WAIT_PREFIX + "open_additional_resources_accordion")
        await self.browser_manager.page.locator(additional_resource_accordion_selector).click()
        logger.debug(DONE_PREFIX + "open_additional_resources_accordion")

    async def set_lora_weight(self, lora_weight: float):
        logger.debug(WAIT_PREFIX + "set_lora_weight: " + str(lora_weight))
        await self.browser_manager.page.locator(lora_weight_selector).fill(str(lora_weight))
        logger.debug(DONE_PREFIX + "set_lora_weight: " + str(lora_weight))

    async def write_positive_prompt(self, positive_text_prompt: str):
        logger.debug(WAIT_PREFIX + "write_positive_prompt")
        await self.browser_manager.page.get_by_role("textbox", name="Your prompt goes here...").fill(positive_text_prompt)
        logger.debug(DONE_PREFIX + "write_positive_prompt")

    async def write_negative_prompt(self, negative_text_prompt: str):
        async def interact():
            await self.browser_manager.page.get_by_role("textbox", name="Negative Prompt").fill(negative_text_prompt)

        await try_action("write_negative_prompt", interact)

    async def set_ratio_by_text(self, ratio_text: str):
        logger.debug(WAIT_PREFIX + "set_ratio_by_text: " + ratio_text)
        await self.browser_manager.page.locator("label").filter(has_text=ratio_text).click()
        logger.debug(DONE_PREFIX + "set_ratio_by_text: " + ratio_text)

    async def toggle_image_properties_accordion(self):
        logger.debug(WAIT_PREFIX + "toggle_image_properties_accordion")
        await self.browser_manager.page.get_by_role("button", name="Advanced").click()
        logger.debug(DONE_PREFIX + "toggle_image_properties_accordion")

    async def set_cfg_scale(self, cfg_scale: float):
        async def interact():
            await self.browser_manager.page.locator(cfg_scale_input_selector).wait_for(
                timeout=INTERACTION_TIMEOUT)
            await self.browser_manager.page.locator(cfg_scale_input_selector).fill(str(cfg_scale))

        await try_action('set_cfg_scale: ' + str(cfg_scale), interact)

    async def set_sampler(self, sampler: str):
        logger.debug(WAIT_PREFIX + "set_sampler: " + sampler)
        await self.browser_manager.page.locator(sampler_input_selector).click()
        sampler_option_selector: str = sampler_option_selector_prefix + sampler + sampler_option_selector_suffix
        await self.browser_manager.page.locator(sampler_option_selector).click()
        logger.debug(DONE_PREFIX + "set_sampler: " + sampler)

    async def set_steps(self, steps: int):
        logger.debug(WAIT_PREFIX + "set_steps: " + str(steps))
        await self.browser_manager.page.locator(steps_input_selector).fill(str(steps))
        logger.debug(DONE_PREFIX + "set_steps: " + str(steps))

    async def set_seed(self, seed: str):
        logger.debug(WAIT_PREFIX + "set_seed: " + seed)
        await self.browser_manager.page.get_by_role("textbox", name="Random").fill(seed)
        logger.debug(DONE_PREFIX + "set_seed: " + seed)

    async def inject(self, prompt: Prompt, inject_seed: bool):
        await self.add_resource(prompt.base_model)
        await self.open_additional_resources_accordion()
        await asyncio.sleep(2)
        for lora_weight in prompt.lora_weights:
            await self.add_resource(lora_weight.lora)
            await self.set_lora_weight(lora_weight.weight)
        for embedding in prompt.embeddings:
            await self.add_resource(embedding)
        if prompt.vae is not None:
            await self.add_resource(prompt.vae)
        await self.write_positive_prompt(prompt.positive_prompt_text)
        if prompt.negative_prompt_text is not None:
            await self.write_negative_prompt(prompt.negative_prompt_text)
        await self.set_ratio_by_text(prompt.ratio_selector_text)
        await self.toggle_image_properties_accordion()
        await self.set_cfg_scale(prompt.cfg_scale)
        await self.set_sampler(prompt.sampler_name)
        await self.set_steps(prompt.generation_steps)
        if prompt.seed is not None and inject_seed:
            await self.set_seed(prompt.seed)
