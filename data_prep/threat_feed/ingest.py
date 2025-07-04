from .schema import ThreatFeedRecord
from typing import List

def ingest_threat_feed(raw_data: List[dict]) -> List[ThreatFeedRecord]:
    return [ThreatFeedRecord(**item) for item in raw_data]
