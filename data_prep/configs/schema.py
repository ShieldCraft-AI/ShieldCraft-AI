from pydantic import BaseModel
from typing import Optional


class ConfigRecord(BaseModel):
    config_id: str
    version: str
    content: dict
    updated_at: str
    description: Optional[str]
