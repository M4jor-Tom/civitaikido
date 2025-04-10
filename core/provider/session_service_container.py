import asyncio

from core.model.injection_extraction_state import InjectionExtractionState
from core.service import StateManager, BrowserManager, PromptBuilder, PromptTreeBuilder, ProfilePreparator, \
    PromptInjector, BuzzCollector, ImageGenerator, ImageExtractor, RoutineExecutor, SceneManager

import logging

logger = logging.getLogger(__name__)

class SessionServiceContainer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state_manager: StateManager = StateManager(InjectionExtractionState.INIT)
        self.browser_manager: BrowserManager = BrowserManager()
        self.prompt_tree_builder: PromptTreeBuilder = PromptTreeBuilder()
        self.scene_manager: SceneManager = SceneManager(
            session_id=session_id,
            state_manager=self.state_manager,
            browser_manager=self.browser_manager,
            prompt_tree_builder=self.prompt_tree_builder
        )
        self.profile_preparator: ProfilePreparator = ProfilePreparator(self.browser_manager)
        self.prompt_builder: PromptBuilder = PromptBuilder()
        self.prompt_injector = PromptInjector(self.browser_manager)
        self.buzz_collector = BuzzCollector(self.browser_manager, self.profile_preparator)
        self.image_generator = ImageGenerator(self.browser_manager)
        self.image_extractor = ImageExtractor(self.browser_manager)
        self.routine_executor = RoutineExecutor(
            state_manager=self.state_manager,
            browser_manager=self.browser_manager,
            image_extractor=self.image_extractor,
            image_generator=self.image_generator,
            prompt_injector=self.prompt_injector,
            profile_preparator=self.profile_preparator,
            prompt_tree_builder=self.prompt_tree_builder,
            prompt_builder=self.prompt_builder
        )

    def init(self):
        asyncio.create_task(self.browser_manager.init_browser())

    async def shutdown(self):
        logger.info(f"Exited scene: {await self.scene_manager.build_scene()}")
        await self.browser_manager.shutdown_if_possible()
