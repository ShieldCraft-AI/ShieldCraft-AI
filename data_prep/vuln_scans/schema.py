from pydantic import BaseModel
from typing import Optional

class VulnScanRecord(BaseModel):
    scan_id: str
    asset_id: str
    vulnerability: str
    severity: str
    detected_at: str
    status: Optional[str]
    details: Optional[dict]
