from pydantic import BaseModel
from typing import Optional


class AssetRecord(BaseModel):
    asset_id: str
    type: str
    hostname: Optional[str]
    ip_address: Optional[str]
    owner: Optional[str]
    tags: Optional[list]
    metadata: Optional[dict]
