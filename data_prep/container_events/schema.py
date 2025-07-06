from pydantic import BaseModel
from typing import Optional


class ContainerEventRecord(BaseModel):
    event_id: str
    container_id: str
    image: Optional[str]
    event_type: str
    timestamp: str
    details: Optional[dict]
