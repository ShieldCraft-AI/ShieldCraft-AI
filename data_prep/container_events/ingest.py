from .schema import ContainerEventRecord
from typing import List


def ingest_container_events(raw_data: List[dict]) -> List[ContainerEventRecord]:
    return [ContainerEventRecord(**item) for item in raw_data]
