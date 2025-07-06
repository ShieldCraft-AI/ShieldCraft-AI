from pydantic import BaseModel
from typing import Optional


class UserIdentityRecord(BaseModel):
    user_id: str
    username: str
    email: Optional[str]
    groups: Optional[list]
    roles: Optional[list]
    last_login: Optional[str]
    status: Optional[str]
