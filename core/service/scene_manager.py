from core.model import Scene
from core.service import StateManager, BrowserManager, PromptTreeBuilder


class SceneManager:
    def __init__(self, session_id: str, state_manager: StateManager, browser_manager: BrowserManager, prompt_tree_builder: PromptTreeBuilder):
        self.session_id: str = session_id
        self.state_manager: StateManager = state_manager
        self.browser_manager: BrowserManager = browser_manager
        self.prompt_tree_builder: PromptTreeBuilder = prompt_tree_builder

    async def build_scene(self) -> Scene:
        return Scene(
            session_id=self.session_id,
            civitai_url=self.browser_manager.signed_in_civitai_generation_url,
            injected_file=self.prompt_tree_builder.file,
            injection_extraction_state=self.state_manager.injection_extraction_state.value
        )
