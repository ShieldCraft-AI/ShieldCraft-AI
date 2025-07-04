from pydantic import BaseModel
from typing import Optional

class EndpointTelemetryRecord(BaseModel):
    endpoint_id: str
    hostname: str
    os: Optional[str]
    ip_address: Optional[str]
    user: Optional[str]
    event_type: str
    event_time: str
    details: Optional[dict]
