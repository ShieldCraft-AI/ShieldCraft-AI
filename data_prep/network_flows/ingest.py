from .schema import NetworkFlowRecord
from typing import List


def ingest_network_flows(raw_data: List[dict]) -> List[NetworkFlowRecord]:
    return [NetworkFlowRecord(**item) for item in raw_data]
