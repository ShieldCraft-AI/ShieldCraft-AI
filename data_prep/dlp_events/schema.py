from pydantic import BaseModel
from typing import Optional


class DLPEventRecord(BaseModel):
    event_id: str
    source: str
    event_type: str
    timestamp: str
    user: Optional[str]
    file_name: Optional[str]
    action: Optional[str]
    details: Optional[dict]
