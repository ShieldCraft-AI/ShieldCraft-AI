from pydantic import BaseModel
from typing import Optional


class AlertRecord(BaseModel):
    alert_id: str
    source: str
    type: str
    severity: str
    timestamp: str
    description: Optional[str]
    details: Optional[dict]
