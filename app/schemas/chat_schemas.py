from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessage(BaseModel):
    sender: str  # "user" or "bot"
    text: str
    timestamp: datetime

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    ticket_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    chat_history: List[Dict[str, str]] = Field(default_factory=list)  # Serialized chat history
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatResponse(BaseModel):
    session_id: str
    user_id: str
    ticket_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    chat_history: List[Dict[str, str]] = Field(default_factory=list)  # Serialized chat history
    created_at: datetime 
    updated_at: datetime 

class ChatView(BaseModel):
    session_id: str
    user_id: str
    ticket_id: Optional[str] = None
    chat_history: List[Dict[str, str]] = Field(default_factory=list)  # Serialized chat history
    created_at: datetime 
    updated_at: datetime 


class ChatList(BaseModel):
    session_id: str
    user_id: str
    ticket_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime