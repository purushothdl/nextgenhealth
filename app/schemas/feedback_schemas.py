from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Feedback(BaseModel):
    feedback_id: str
    user_id: str
    user_role: str  # 'patient', 'doctor', or 'admin'
    rating: int
    comment: str
    timestamp: datetime