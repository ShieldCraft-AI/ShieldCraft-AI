from .schema import APIGatewayLogRecord
from typing import List


def ingest_api_gateway_logs(raw_data: List[dict]) -> List[APIGatewayLogRecord]:
    return [APIGatewayLogRecord(**item) for item in raw_data]
