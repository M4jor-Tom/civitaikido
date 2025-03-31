# src/app.py

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config import PROFILE
from src.rest import (
    browser_management_router,
    image_generation_router,
    prompt_injection_router,
    image_extraction_router,
    routine_router
)
from src.provider import get_browser_manager

logger = logging.getLogger(__name__)
browser_manager = get_browser_manager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Civitaikido is starting with profile [{PROFILE}]...")
    asyncio.create_task(browser_manager.init_browser())
    yield
    await browser_manager.shutdown_if_possible()

app = FastAPI(lifespan=lifespan)

app.include_router(browser_management_router)
app.include_router(image_generation_router)
app.include_router(prompt_injection_router)
app.include_router(image_extraction_router)
app.include_router(routine_router)
