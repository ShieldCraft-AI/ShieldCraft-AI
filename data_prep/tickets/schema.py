from pydantic import BaseModel
from typing import Optional

class TicketRecord(BaseModel):
    ticket_id: str
    source: str
    created_at: str
    updated_at: Optional[str]
    status: str
    priority: Optional[str]
    assigned_to: Optional[str]
    description: Optional[str]
    tags: Optional[list]
