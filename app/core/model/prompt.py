import hashlib

from pydantic import BaseModel, computed_field
from core.model.resource import Resource
from core.model.lora_weight import LoraWeight

class Prompt(BaseModel):
    base_model: Resource
    lora_weights: list[LoraWeight]
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

    def get_hash(self) -> str:
        return 'md5-' + hashlib.md5(str(self).encode()).hexdigest()

    @computed_field
    @property
    def ratio_selector_text(self) -> str:
        if self.image_width_px == 832 and self.image_height_px == 1216:
            return 'Portrait832x1216'
        elif self.image_width_px == 1216 and self.image_height_px == 832:
            return 'Landscape1216x832'
        elif self.image_width_px == 1024 and self.image_height_px == 1024:
            return 'Square1024x1024'
        raise TypeError(f"Dimensions {self.image_width_px} x {self.image_height_px} unknown for civitai generation selection")
