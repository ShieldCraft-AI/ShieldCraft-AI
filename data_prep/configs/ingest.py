from .schema import ConfigRecord
from typing import List

def ingest_configs(raw_data: List[dict]) -> List[ConfigRecord]:
    return [ConfigRecord(**item) for item in raw_data]
