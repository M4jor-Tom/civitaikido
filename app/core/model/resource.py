from pydantic import BaseModel

class Resource(BaseModel):
    hash: str
    page_url: str | None
