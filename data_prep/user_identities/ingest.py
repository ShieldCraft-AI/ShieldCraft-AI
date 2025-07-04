from .schema import UserIdentityRecord
from typing import List

def ingest_user_identities(raw_data: List[dict]) -> List[UserIdentityRecord]:
    return [UserIdentityRecord(**item) for item in raw_data]
