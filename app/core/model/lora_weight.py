from pydantic import BaseModel
from core.model.resource import Resource

class LoraWeight(BaseModel):
    lora: Resource
    weight: float
