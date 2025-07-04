from .schema import OSINTRecord
from typing import List

def ingest_osint(raw_data: List[dict]) -> List[OSINTRecord]:
    return [OSINTRecord(**item) for item in raw_data]
