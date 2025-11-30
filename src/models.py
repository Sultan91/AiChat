# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from src.database import Base

# This will help prevent table redefinition issues
metadata = Base.metadata

# Clear any existing tables from metadata to prevent redefinition
metadata.clear()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    __table_args__ = {'extend_existing': True}  # Allow table extension if it exists

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}  # Allow table extension if it exists

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {'extend_existing': True}  # Allow table extension if it exists

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

# This ensures tables are created only once
@event.listens_for(Base.metadata, 'before_create')
def receive_before_create(target, connection, **kw):
    # Clear any existing tables from metadata to prevent redefinition
    Base.metadata.clear()