import asyncio

from fastapi import UploadFile

from core.config import GENERATION_DEFAULT_DIR
from core.model.injection_extraction_state import InjectionExtractionState
from core.service import StateManager, BrowserManager, CivitaiPagePreparator, XmlParser, PromptBuilder, PromptInjector, \
    ImageGenerator, ImageExtractor, PopupRemover


class RoutineExecutor:
    def __init__(self,
                state_manager: StateManager,
                browser_manager: BrowserManager,
                civitai_page_preparator: CivitaiPagePreparator,
                xml_parser: XmlParser,
                prompt_builder: PromptBuilder,
                prompt_injector: PromptInjector,
                image_generator: ImageGenerator,
                image_extractor: ImageExtractor,
                popup_remover: PopupRemover):
        self.state_manager = state_manager
        self.browser_manager = browser_manager
        self.civitai_page_preparator = civitai_page_preparator
        self.xml_parser = xml_parser
        self.prompt_builder = prompt_builder
        self.prompt_injector = prompt_injector
        self.image_generator = image_generator
        self.image_extractor = image_extractor
        self.popup_remover = popup_remover
    async def execute_routine(self,
                            session_url: str,
                            file: UploadFile,
                            inject_seed: bool = False,
                            close_browser_when_finished: bool = True):
        ask_first_session_preparation: bool = True
        await self.browser_manager.open_browser(session_url)
        async def interact():
            await self.civitai_page_preparator.prepare_civitai_page(ask_first_session_preparation)
            self.state_manager.injection_extraction_state = InjectionExtractionState.PAGE_PREPARED
            await self.prompt_injector.inject(self.prompt_builder.build_from_xml(await self.xml_parser.parse_xml(file)), inject_seed)
            self.state_manager.injection_extraction_state = InjectionExtractionState.PROMPT_INJECTED
            await self.image_generator.generate_all_possible()
            self.state_manager.injection_extraction_state = InjectionExtractionState.IMAGES_GENERATED
            await self.image_extractor.save_images_from_page(
                GENERATION_DEFAULT_DIR + "/" + str(file.filename).split('.xml')[0])
            self.state_manager.injection_extraction_state = InjectionExtractionState.IMAGES_EXTRACTED
            if close_browser_when_finished:
                await self.browser_manager.shutdown_if_possible()
        await asyncio.gather(
            self.popup_remover.remove_popups(ask_first_session_preparation),
            interact()
        )