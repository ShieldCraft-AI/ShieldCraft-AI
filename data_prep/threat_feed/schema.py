from pydantic import BaseModel
from typing import Optional

class ThreatFeedRecord(BaseModel):
    feed_id: str
    indicator: str
    type: str
    first_seen: str
    last_seen: Optional[str]
    confidence: Optional[int]
