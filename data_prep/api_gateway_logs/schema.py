from pydantic import BaseModel
from typing import Optional


class APIGatewayLogRecord(BaseModel):
    request_id: str
    api_id: str
    resource: str
    method: str
    status_code: int
    timestamp: str
    source_ip: Optional[str]
    user_agent: Optional[str]
    details: Optional[dict]
