import logging

from fastapi import UploadFile

from core.config import GENERATION_DEFAULT_DIR
from core.model import FileSceneDto, build_generation_path_from_generation_dir_and_file
from core.model.injection_extraction_state import InjectionExtractionState
from core.service import StateManager, BrowserManager, ProfilePreparator, PromptTreeBuilder, PromptBuilder, PromptInjector, \
    ImageGenerator, ImageExtractor

logger = logging.getLogger(__name__)

class RoutineExecutor:
    def __init__(self,
                 state_manager: StateManager,
                 browser_manager: BrowserManager,
                 profile_preparator: ProfilePreparator,
                 prompt_tree_builder: PromptTreeBuilder,
                 prompt_builder: PromptBuilder,
                 prompt_injector: PromptInjector,
                 image_generator: ImageGenerator,
                 image_extractor: ImageExtractor):
        self.state_manager: StateManager = state_manager
        self.browser_manager: BrowserManager = browser_manager
        self.profile_preparator: ProfilePreparator = profile_preparator
        self.prompt_tree_builder: PromptTreeBuilder = prompt_tree_builder
        self.prompt_builder: PromptBuilder = prompt_builder
        self.prompt_injector: PromptInjector = prompt_injector
        self.image_generator: ImageGenerator = image_generator
        self.image_extractor: ImageExtractor = image_extractor

    async def finite_state_machine(self,
                                   close_browser_when_finished: bool,
                                   file: UploadFile,
                                   inject_seed: bool = False,
                                   overridden_state: InjectionExtractionState | None = None):
        generation_path: str = build_generation_path_from_generation_dir_and_file(GENERATION_DEFAULT_DIR, file)
        file_scene_dto: FileSceneDto = FileSceneDto(generation_path=generation_path)
        if overridden_state:
            logger.info(f"Overriding entry state to {overridden_state}")
            self.state_manager.update_injection_extraction_state(overridden_state)
        while self.state_manager.injection_extraction_state != InjectionExtractionState.TERMINATED:
            if self.state_manager.injection_extraction_state == InjectionExtractionState.INIT:
                await self.profile_preparator.prepare_profile()
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.PROFILE_PREPARED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.PROFILE_PREPARED:
                await self.prompt_injector.inject(self.prompt_builder.build_from_xml(await self.prompt_tree_builder.build_prompt_tree(file, file_scene_dto)), inject_seed)
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.PROMPT_INJECTED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.PROMPT_INJECTED:
                await self.image_generator.launch_all_possible_generations()
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.IMAGES_GENERATION_LAUNCHED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.IMAGES_GENERATION_LAUNCHED:
                await self.image_extractor.save_images_from_page(generation_path)
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.IMAGES_EXTRACTED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.IMAGES_EXTRACTED:
                if close_browser_when_finished:
                    await self.browser_manager.shutdown_if_possible()
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.TERMINATED)
    async def execute_routine(self,
                              session_url: str,
                              file: UploadFile,
                              inject_seed: bool = False,
                              close_browser_when_finished: bool = True,
                              overridden_state: InjectionExtractionState | None = None):
        await self.browser_manager.open_browser(session_url)
        await self.finite_state_machine(close_browser_when_finished,
                                      file,
                                      inject_seed,
                                      overridden_state)
