from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Feedback(BaseModel):
    feedback_id: str
    user_id: str
    username: str
    user_role: str  # 'patient', 'doctor', or 'admin'
    title: str
    rating: float
    comment: str
    timestamp: datetime