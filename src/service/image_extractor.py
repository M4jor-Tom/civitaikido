from playwright.async_api import async_playwright
import requests
import os
from urllib.parse import urlparse

from src.config import images_selector


class ImageExtractor:
    page: any

    def __init__(self, page):
        self.page = page

    async def enter_feed_view(self):
        await self.page.locator("//*[text()='Feed']").first.click()

    async def save_images_from_page(self, output_dir) -> None:
        """Save all image files from a web page using Playwright.

        Args:
            url: The URL of the web page to scrape images from.
            output_dir: Directory where images will be saved.
        """
        await self.enter_feed_view()
        os.makedirs(output_dir, exist_ok=True)
        img_elements = await self.page.locator(images_selector).all()
        for i, img in enumerate(img_elements):
            src = await img.get_attribute("src")
            if not src:
                continue
            # Make sure to handle relative URLs
            # img_url = urljoin(url, src)
            img_url = src
            try:
                response = requests.get(img_url)
                response.raise_for_status()
                # Extract a filename from the URL or fallback to index
                filename = os.path.basename(urlparse(img_url).path) or f"image_{i}.jpg"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"Saved: {filepath}")
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
