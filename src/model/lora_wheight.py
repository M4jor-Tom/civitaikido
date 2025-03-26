from pydantic import BaseModel
from src.model.resource import Resource

class LoraWheight(BaseModel):
    lora: Resource
    wheight: float
