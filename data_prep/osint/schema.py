from pydantic import BaseModel
from typing import Optional

class OSINTRecord(BaseModel):
    record_id: str
    source: str
    indicator: str
    type: str
    first_seen: Optional[str]
    last_seen: Optional[str]
    confidence: Optional[int]
    details: Optional[dict]
