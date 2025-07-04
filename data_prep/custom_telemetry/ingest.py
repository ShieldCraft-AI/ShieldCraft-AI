from .schema import CustomTelemetryRecord
from typing import List

def ingest_custom_telemetry(raw_data: List[dict]) -> List[CustomTelemetryRecord]:
    return [CustomTelemetryRecord(**item) for item in raw_data]
