from enum import Enum
from typing import Optional
from pydantic import BaseModel



# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None