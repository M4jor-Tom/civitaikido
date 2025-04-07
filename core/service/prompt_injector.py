from core.constant import model_search_input_selector, WAIT_PREFIX, DONE_PREFIX
from core.model import Prompt, Resource
from .browser_manager import BrowserManager
import logging
import asyncio

from core.util import try_action, enter_generation_perspective
from ..config import GLOBAL_TIMEOUT

logger = logging.getLogger(__name__)

class PromptInjector:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def add_resource(self, resource: Resource):
        if resource.page_url is None:
            await self.add_resource_by_hash(resource_hash=resource.hash)
        else:
            await self.add_resource_by_page_url(page_url=resource.page_url)

    async def add_resource_by_page_url(self, page_url: str):
        logger.info(WAIT_PREFIX + "add_resource_by_page_url: " + page_url)
        await self.browser_manager.init_page(page_url)
        await self.browser_manager.page.locator('button[data-activity="create:model"]').wait_for(timeout=GLOBAL_TIMEOUT)
        await self.browser_manager.page.locator('button[data-activity="create:model"]').click()
        await enter_generation_perspective(self.browser_manager.page)
        logger.info(DONE_PREFIX + "add_resource_by_page_url: " + page_url)


    async def add_resource_by_hash(self, resource_hash: str):
        logger.info(WAIT_PREFIX + "add_resource_by_hash: " + resource_hash)
        await self.browser_manager.page.locator(model_search_input_selector).fill(resource_hash)
        await asyncio.sleep(5)
        await self.browser_manager.page.locator("img[src][class][style][alt][loading]").last.click(force=True)
        await self.browser_manager.page.locator('button[data-activity="create:model"]').wait_for(timeout=GLOBAL_TIMEOUT)
        await self.browser_manager.page.locator('button[data-activity="create:model"]').click()
        await enter_generation_perspective(self.browser_manager.page)
        logger.info(DONE_PREFIX + "add_resource_by_hash: " + resource_hash)

    async def open_additional_resources_accordion(self, ):
        logger.info(WAIT_PREFIX + "open_additional_resources_accordion")
        await self.browser_manager.page.locator("//*[text()='Additional Resources']").click()
        logger.info(DONE_PREFIX + "open_additional_resources_accordion")

    async def set_lora_weight(self, lora_weight: float):
        logger.info(WAIT_PREFIX + "set_lora_weight: " + str(lora_weight))
        await self.browser_manager.page.locator(
            "(//*[div/div/div/div/text()='Additional Resources']/following-sibling::*//input[@type][@max][@min][@step][@inputmode])[1]").fill(
            str(lora_weight))
        logger.info(DONE_PREFIX + "set_lora_weight: " + str(lora_weight))

    async def write_positive_prompt(self, positive_text_prompt: str):
        logger.info(WAIT_PREFIX + "write_positive_prompt")
        await self.browser_manager.page.get_by_role("textbox", name="Your prompt goes here...").fill(positive_text_prompt)
        logger.info(DONE_PREFIX + "write_positive_prompt")

    async def write_negative_prompt(self, negative_text_prompt: str):
        async def interact():
            await self.browser_manager.page.get_by_role("textbox", name="Negative Prompt").fill(negative_text_prompt)

        await try_action("write_negative_prompt", interact)

    async def set_ratio_by_text(self, ratio_text: str):
        logger.info(WAIT_PREFIX + "set_ratio_by_text: " + ratio_text)
        await self.browser_manager.page.locator("label").filter(has_text=ratio_text).click()
        logger.info(DONE_PREFIX + "set_ratio_by_text: " + ratio_text)

    async def toggle_image_properties_accordion(self):
        logger.info(WAIT_PREFIX + "toggle_image_properties_accordion")
        await self.browser_manager.page.get_by_role("button", name="Advanced").click()
        logger.info(DONE_PREFIX + "toggle_image_properties_accordion")

    async def set_cfg_scale(self, cfg_scale: float):
        async def interact():
            await self.browser_manager.page.locator("#input_cfgScale-label + div > :nth-child(2) input").wait_for(
                timeout=GLOBAL_TIMEOUT)
            await self.browser_manager.page.locator("#input_cfgScale-label + div > :nth-child(2) input").fill(str(cfg_scale))

        await try_action('set_cfg_scale: ' + str(cfg_scale), interact)

    async def set_sampler(self, sampler: str):
        logger.info(WAIT_PREFIX + "set_sampler: " + sampler)
        await self.browser_manager.page.locator("#input_sampler").click()
        await self.browser_manager.page.locator(
            "//div[@role='combobox']/following-sibling::div//div[text()='" + sampler + "']").click()
        logger.info(DONE_PREFIX + "set_sampler: " + sampler)

    async def set_steps(self, steps: int):
        logger.info(WAIT_PREFIX + "set_steps: " + str(steps))
        await self.browser_manager.page.locator("#input_steps-label + div > :nth-child(2) input").fill(str(steps))
        logger.info(DONE_PREFIX + "set_steps: " + str(steps))

    async def set_seed(self, seed: str):
        logger.info(WAIT_PREFIX + "set_seed: " + seed)
        await self.browser_manager.page.get_by_role("textbox", name="Random").fill(seed)
        logger.info(DONE_PREFIX + "set_seed: " + seed)

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
        ratio_selector_text: str | None = prompt.ratio_selector_text
        if ratio_selector_text is not None:
            await self.set_ratio_by_text(ratio_selector_text)
        await self.toggle_image_properties_accordion()
        await self.set_cfg_scale(prompt.cfg_scale)
        await self.set_sampler(prompt.sampler_name)
        await self.set_steps(prompt.generation_steps)
        if prompt.seed is not None and inject_seed:
            await self.set_seed(prompt.seed)
