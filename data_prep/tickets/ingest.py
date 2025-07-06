from .schema import TicketRecord
from typing import List


def ingest_tickets(raw_data: List[dict]) -> List[TicketRecord]:
    return [TicketRecord(**item) for item in raw_data]
