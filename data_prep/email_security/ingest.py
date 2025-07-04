from .schema import EmailSecurityRecord
from typing import List

def ingest_email_security(raw_data: List[dict]) -> List[EmailSecurityRecord]:
    return [EmailSecurityRecord(**item) for item in raw_data]
