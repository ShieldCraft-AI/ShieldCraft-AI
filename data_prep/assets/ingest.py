from .schema import AssetRecord
from typing import List

def ingest_assets(raw_data: List[dict]) -> List[AssetRecord]:
    return [AssetRecord(**item) for item in raw_data]
