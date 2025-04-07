import asyncio

from core.model.injection_extraction_state import InjectionExtractionState
from core.service import StateManager, BrowserManager, PromptBuilder, XmlParser, CivitaiPagePreparator, PopupRemover, \
    PromptInjector, BuzzCollector, ImageGenerator, ImageExtractor, RoutineExecutor

class SessionServiceContainer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state_manager: StateManager = StateManager(InjectionExtractionState.IDLE)
        self.browser_manager: BrowserManager = BrowserManager(self.state_manager)
        self.civitai_page_preparator: CivitaiPagePreparator = CivitaiPagePreparator(self.browser_manager)
        self.popup_remover: PopupRemover = PopupRemover(self.browser_manager)
        self.xml_parser: XmlParser = XmlParser()
        self.prompt_builder: PromptBuilder = PromptBuilder()
        self.prompt_injector = PromptInjector(self.browser_manager)
        self.buzz_collector = BuzzCollector(self.browser_manager, self.civitai_page_preparator, self.popup_remover)
        self.image_generator = ImageGenerator(self.browser_manager)
        self.image_extractor = ImageExtractor(self.browser_manager)
        self.routine_executor = RoutineExecutor(
            state_manager=self.state_manager,
            popup_remover=self.popup_remover,
            browser_manager=self.browser_manager,
            image_extractor=self.image_extractor,
            image_generator=self.image_generator,
            prompt_injector=self.prompt_injector,
            civitai_page_preparator=self.civitai_page_preparator,
            xml_parser=self.xml_parser,
            prompt_builder=self.prompt_builder
        )

    def init(self):
        asyncio.create_task(self.browser_manager.init_browser())

    async def shutdown(self):
        await self.browser_manager.shutdown_if_possible()
