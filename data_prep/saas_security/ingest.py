from .schema import SaaSSecurityRecord
from typing import List


def ingest_saas_security(raw_data: List[dict]) -> List[SaaSSecurityRecord]:
    return [SaaSSecurityRecord(**item) for item in raw_data]
