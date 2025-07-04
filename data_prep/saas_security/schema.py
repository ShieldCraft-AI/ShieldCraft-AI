from pydantic import BaseModel
from typing import Optional

class SaaSSecurityRecord(BaseModel):
    event_id: str
    service: str
    user: Optional[str]
    event_type: str
    timestamp: str
    details: Optional[dict]
