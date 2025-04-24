from functools import lru_cache

from fastapi import Depends

from core.constant import DEFAULT_SESSION_ID
from core.provider import SessionServiceRegistry, SessionServiceContainer
from core.service import StateManager, BrowserManager, ProfilePreparator, PromptTreeBuilder, PromptBuilder, \
    PromptInjector, BuzzCollector, ImageGenerator, ImageExtractor, RoutineExecutor

service_registry = SessionServiceRegistry()

@lru_cache
def get_session_service_registry() -> SessionServiceRegistry:
    return service_registry

async def get_state_manager(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> StateManager:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.state_manager

async def get_browser_manager(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> BrowserManager:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.browser_manager

async def get_profile_preparator(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> ProfilePreparator:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.profile_preparator

async def get_prompt_tree_builder(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> PromptTreeBuilder:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.prompt_tree_builder

async def get_prompt_builder(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> PromptBuilder:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.prompt_builder

async def get_prompt_injector(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> PromptInjector:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.prompt_injector

async def get_buzz_collector(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> BuzzCollector:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.buzz_collector

async def get_image_generator(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> ImageGenerator:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.image_generator

async def get_image_extractor(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry),
) -> ImageExtractor:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.image_extractor

async def get_routine_executor(
    session_id: str = DEFAULT_SESSION_ID,
    registry: SessionServiceRegistry = Depends(get_session_service_registry)
) -> RoutineExecutor:
    container: SessionServiceContainer = await registry.get_or_create(session_id)
    return container.routine_executor
