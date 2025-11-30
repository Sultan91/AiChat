from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field

# Base schemas
class MessageBase(BaseModel):
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")

class ChatSessionBase(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    created_at: Optional[datetime] = Field(None, description="Timestamp when session was created")

class DocumentBase(BaseModel):
    filename: str = Field(..., description="Name of the document")
    content: str = Field(..., description="Content of the document")
    added_at: Optional[datetime] = Field(None, description="Timestamp when document was added")

# Request schemas
class MessageCreate(MessageBase):
    pass

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Existing session ID. If not provided, a new session will be created")
    message: str = Field(..., description="User's message content")

# Response schemas
class MessageOut(MessageBase):
    id: int
    created_at: datetime
    session_id: int

    class Config:
        from_attributes = True

class ChatSessionOut(ChatSessionBase):
    id: int
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True

class DocumentOut(DocumentBase):
    id: int

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI's response message")
    session_id: str = Field(..., description="Session ID for continuing the conversation")
    history: List[MessageOut] = Field(default_factory=list, description="Message history for this session")
