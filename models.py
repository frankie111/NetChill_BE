from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    uid: str
    username: Optional[str] = None
    email: str
    is_admin: bool = False
