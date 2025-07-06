from .schema import EndpointTelemetryRecord
from typing import List


def ingest_endpoint_telemetry(raw_data: List[dict]) -> List[EndpointTelemetryRecord]:
    return [EndpointTelemetryRecord(**item) for item in raw_data]
