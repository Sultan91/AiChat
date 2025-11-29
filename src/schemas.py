from pydantic import BaseModel
from typing import List

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageOut(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    history: List[MessageOut]
