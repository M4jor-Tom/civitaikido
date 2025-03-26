from pydantic import BaseModel, computed_field
from src.model.resource import Resource
from src.model.lora_wheight import LoraWheight

class Prompt(BaseModel):
    base_model: Resource
    loraWheights: list[LoraWheight]
    embeddings: list[Resource]
    vae: Resource | None
    positive_prompt_text: str
    negative_prompt_text: str | None
    image_width_px: int
    image_height_px: int
    generation_steps: int
    sampler_name: str
    cfg_scale: float
    seed: str | None
    clip_skip: int

    @computed_field
    @property
    def ratio_selector_text(self) -> str | None:
        if self.image_width_px == 832 and self.image_height_px == 1216:
            return 'Portrait832x1216'
        elif self.image_width_px == 1216 and self.image_height_px == 832:
            return 'Landscape1216x832'
        elif self.image_width_px == 1024 and self.image_height_px == 1024:
            return 'Square1024x1024'
        return None
