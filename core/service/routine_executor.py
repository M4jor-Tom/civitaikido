import asyncio
import logging

from fastapi import UploadFile

from core.config import GENERATION_DEFAULT_DIR
from core.model.injection_extraction_state import InjectionExtractionState
from core.service import StateManager, BrowserManager, ProfilePreparator, XmlParser, PromptBuilder, PromptInjector, \
    ImageGenerator, ImageExtractor

logger = logging.getLogger(__name__)

inconsistent_state_message: str = f"Entered finite state machine at {InjectionExtractionState.INIT.value} state, while it "\
                                  f"should only be entered at {InjectionExtractionState.BROWSER_OPEN.value} state. "\
                                  f"Terminating now"
class RoutineExecutor:
    def __init__(self,
                 state_manager: StateManager,
                 browser_manager: BrowserManager,
                 profile_preparator: ProfilePreparator,
                 xml_parser: XmlParser,
                 prompt_builder: PromptBuilder,
                 prompt_injector: PromptInjector,
                 image_generator: ImageGenerator,
                 image_extractor: ImageExtractor):
        self.state_manager: StateManager = state_manager
        self.browser_manager: BrowserManager = browser_manager
        self.profile_preparator: ProfilePreparator = profile_preparator
        self.xml_parser: XmlParser = xml_parser
        self.prompt_builder: PromptBuilder = prompt_builder
        self.prompt_injector: PromptInjector = prompt_injector
        self.image_generator: ImageGenerator = image_generator
        self.image_extractor: ImageExtractor = image_extractor

    async def finite_state_machine(self,
                                   close_browser_when_finished: bool,
                                   file: UploadFile,
                                   inject_seed: bool = False,
                                   overridden_state: InjectionExtractionState | None = None):
        if overridden_state:
            logger.info(f"Overriding entry state to {overridden_state}")
            self.state_manager.update_injection_extraction_state(overridden_state)
        while self.state_manager.injection_extraction_state != InjectionExtractionState.TERMINATED:
            if self.state_manager.injection_extraction_state == InjectionExtractionState.INIT:
                logger.error(inconsistent_state_message)
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.TERMINATED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.BROWSER_OPEN:
                await self.profile_preparator.prepare_profile()
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.PROFILE_PREPARED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.PROFILE_PREPARED:
                await self.prompt_injector.inject(self.prompt_builder.build_from_xml(await self.xml_parser.parse_xml(file)), inject_seed)
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.PROMPT_INJECTED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.PROMPT_INJECTED:
                await self.image_generator.generate_all_possible()
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.IMAGES_GENERATED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.IMAGES_GENERATED:
                await self.image_extractor.save_images_from_page(
                    GENERATION_DEFAULT_DIR + "/" + str(file.filename).split('.xml')[0])
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.IMAGES_EXTRACTED)
            elif self.state_manager.injection_extraction_state == InjectionExtractionState.IMAGES_EXTRACTED:
                if close_browser_when_finished:
                    await self.browser_manager.shutdown_if_possible()
                self.state_manager.update_injection_extraction_state(InjectionExtractionState.TERMINATED)
    async def execute_routine(self,
                              session_url: str,
                              file: UploadFile,
                              open_new_browser: bool,
                              inject_seed: bool = False,
                              close_browser_when_finished: bool = True,
                              overridden_state: InjectionExtractionState | None = None):
        if open_new_browser:
            await self.browser_manager.open_browser(session_url)
        await self.finite_state_machine(close_browser_when_finished,
                                      file,
                                      inject_seed,
                                      overridden_state)
