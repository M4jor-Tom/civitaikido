# src/app.py

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config import PROFILE, ROLE
from src.provider import get_browser_manager

logger = logging.getLogger(__name__)
browser_manager = get_browser_manager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Civitaikido is starting with profile [{PROFILE}] and role [{ROLE}]...")
    asyncio.create_task(browser_manager.init_browser())
    yield
    await browser_manager.shutdown_if_possible()

app = FastAPI(lifespan=lifespan)

if PROFILE == "DEV":
    from src.rest import test_router
    app.include_router(test_router)
if ROLE == "BUZZ_RUNNER":
    from src.rest import buzz_picking_router
    app.include_router(buzz_picking_router)
elif ROLE == "INJECTOR_EXTRACTOR":
    from src.rest import routine_router
    app.include_router(routine_router)
    from src.rest import (
        browser_management_router,
        image_generation_router,
        prompt_injection_router,
        image_extraction_router,
    )
    app.include_router(browser_management_router)
    app.include_router(image_generation_router)
    app.include_router(prompt_injection_router)
    app.include_router(image_extraction_router)
