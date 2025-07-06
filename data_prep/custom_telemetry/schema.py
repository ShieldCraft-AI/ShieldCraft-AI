from pydantic import BaseModel
from typing import Optional


class CustomTelemetryRecord(BaseModel):
    record_id: str
    source: str
    event_type: str
    timestamp: str
    payload: Optional[dict]
    tags: Optional[list]
