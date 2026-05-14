from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    session_id: int

class Message(MessageBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatSession(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[Message] = []
    model_config = ConfigDict(from_attributes=True)