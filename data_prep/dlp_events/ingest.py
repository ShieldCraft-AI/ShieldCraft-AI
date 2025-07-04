from .schema import DLPEventRecord
from typing import List

def ingest_dlp_events(raw_data: List[dict]) -> List[DLPEventRecord]:
    return [DLPEventRecord(**item) for item in raw_data]
