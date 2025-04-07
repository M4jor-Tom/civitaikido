import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import PROFILE, ROLE
from core.model import Profile, Role
from core.provider.factory import get_session_service_registry

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Civitaikido is starting with profile [{PROFILE.value}] and role [{ROLE.value}]...")
    yield
    await get_session_service_registry().shutdown_all()

app = FastAPI(lifespan=lifespan)

if PROFILE == Profile.DEV:
    from core.rest import test_router, state_router

    app.include_router(test_router)
if ROLE == Role.buzz_runner:
    from core.rest import buzz_picking_router
    app.include_router(buzz_picking_router)
elif ROLE == Role.injector_extractor:
    from core.rest import routine_router
    app.include_router(routine_router)
    app.include_router(state_router)
    from core.rest import (
        browser_management_router,
        image_generation_router,
        prompt_injection_router,
        image_extraction_router,
    )
    app.include_router(browser_management_router)
    app.include_router(image_generation_router)
    app.include_router(prompt_injection_router)
    app.include_router(image_extraction_router)
