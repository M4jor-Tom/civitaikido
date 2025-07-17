import requests
import os
from urllib.parse import urlparse
import logging

from core.constant import images_selector, all_jobs_done_selector, DONE_PREFIX
from . import BrowserManager
from core.util import enter_feed_view
from ..config import IMAGES_GENERATION_TIMEOUT
from ..util.page_preparation import confirm_start_generating_yellow_button

logger = logging.getLogger(__name__)

class ImageExtractor:
    browser_manager: BrowserManager

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def save_images_from_page(self, output_dir_in_home: str) -> None:
        """Save all image files from a web page using Playwright.

        Args:
            output_dir_in_home: Directory where images will be saved.
        """
        output_dir: str = os.environ['HOME'] + '/' + output_dir_in_home
        await confirm_start_generating_yellow_button(self.browser_manager.page)
        await self.browser_manager.page.locator(all_jobs_done_selector).wait_for(timeout=IMAGES_GENERATION_TIMEOUT)
        await enter_feed_view(self.browser_manager.page)
        os.makedirs(output_dir, exist_ok=True)
        img_elements = await self.browser_manager.page.locator(images_selector).all()
        for i, img in enumerate(img_elements):
            src = await img.get_attribute("src")
            if not src:
                continue
            # Make sure to handle relative URLs
            # img_url = urljoin(url, src)
            img_url = src
            response = requests.get(img_url)
            response.raise_for_status()
            # Extract a filename from the URL or fallback to index
            filename = os.path.basename(urlparse(img_url).path) or f"image_{i}.jpg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            logger.info(DONE_PREFIX + f"Saved: {filepath}")
