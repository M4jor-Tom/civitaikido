from functools import lru_cache

from src.model.injection_extraction_state import InjectionExtractionState
from src.service import BrowserManager, PromptBuilder, XmlParser, CivitaiPagePreparator, ImageGenerator, ImageExtractor, \
    PromptInjector, BuzzCollector, PopupRemover, StateManager

# Services
state_manager: StateManager = StateManager(InjectionExtractionState.IDLE)
browser_manager: BrowserManager = BrowserManager(state_manager)
prompt_builder: PromptBuilder = PromptBuilder()
xml_parser: XmlParser = XmlParser()
civitai_page_preparator: CivitaiPagePreparator = CivitaiPagePreparator(browser_manager)
popup_remover: PopupRemover = PopupRemover(browser_manager)
prompt_injector = PromptInjector(browser_manager, civitai_page_preparator)
buzz_collector = BuzzCollector(browser_manager, civitai_page_preparator, popup_remover)
image_generator = ImageGenerator(browser_manager)
image_extractor = ImageExtractor(browser_manager)

@lru_cache
def get_state_manager() -> StateManager:
    return state_manager
@lru_cache
def get_browser_manager() -> BrowserManager:
    return browser_manager
@lru_cache
def get_prompt_builder() -> PromptBuilder:
    return prompt_builder
@lru_cache
def get_xml_parser() -> XmlParser:
    return xml_parser
@lru_cache
def get_civitai_page_preparator() -> CivitaiPagePreparator:
    return civitai_page_preparator
@lru_cache
def get_popup_remover() -> PopupRemover:
    return popup_remover
@lru_cache
def get_image_generator() -> ImageGenerator:
    return image_generator
@lru_cache
def get_image_extractor() -> ImageExtractor:
    return image_extractor
@lru_cache
def get_prompt_injector() -> PromptInjector:
    return prompt_injector
@lru_cache
def get_buzz_collector() -> BuzzCollector:
    return buzz_collector
