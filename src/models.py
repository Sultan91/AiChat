from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    role = Column(String)  # "user" / "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class Chat():
    pass

