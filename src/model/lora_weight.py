from pydantic import BaseModel
from src.model.resource import Resource

class LoraWeight(BaseModel):
    lora: Resource
    weight: float
