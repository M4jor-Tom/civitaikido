from fastapi import APIRouter, Depends

from src.provider import get_image_extractor
from src.constant import generation_default_dir
from src.service import ImageExtractor

image_extraction_router = APIRouter()

@image_extraction_router.get("/extract_images")
async def extract_images(extraction_dir: str = generation_default_dir,
                         image_extractor: ImageExtractor = Depends(get_image_extractor)):
    await image_extractor.save_images_from_page(extraction_dir)
