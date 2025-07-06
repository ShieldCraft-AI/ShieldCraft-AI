from .schema import VulnScanRecord
from typing import List


def ingest_vuln_scans(raw_data: List[dict]) -> List[VulnScanRecord]:
    return [VulnScanRecord(**item) for item in raw_data]
