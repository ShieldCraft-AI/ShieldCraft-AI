from .schema import AlertRecord
from typing import List


def ingest_alerts(raw_data: List[dict]) -> List[AlertRecord]:
    return [AlertRecord(**item) for item in raw_data]
