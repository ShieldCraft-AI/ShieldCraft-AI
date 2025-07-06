from pydantic import BaseModel
from typing import Optional


class EmailSecurityRecord(BaseModel):
    event_id: str
    timestamp: str
    sender: str
    recipient: str
    subject: Optional[str]
    event_type: str
    verdict: Optional[str]
    details: Optional[dict]
