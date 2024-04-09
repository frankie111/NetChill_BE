from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    uid: str
    username: str
    email: str
    is_admin: bool = False
