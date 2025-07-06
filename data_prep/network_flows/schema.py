from pydantic import BaseModel
from typing import Optional


class NetworkFlowRecord(BaseModel):
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: Optional[str]
    bytes_sent: Optional[int]
    bytes_received: Optional[int]
    timestamp: str
