from pydantic import BaseModel
from core.model import Resource

class LoraWeight(BaseModel):
    lora: Resource
    weight: float
