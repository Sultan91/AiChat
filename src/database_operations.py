from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ChatSession, Message, Document
from src.schemas import MessageOut, DocumentOut


async def create_chat_session(db: AsyncSession, session_id: str) -> ChatSession:
    session = ChatSession(session_id=session_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_chat_session(db: AsyncSession, session_id: str):
    result = await db.execute(select(ChatSession).where(ChatSession.session_id == session_id))
    session = result.scalar_one_or_none()
    return session



async def add_message(db: AsyncSession, session_id: int, role: str, content: str) -> Message:
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_messages(db: AsyncSession, session_id: int) -> List[MessageOut]:
    """
    Get all messages for a session and return them as Pydantic models.
    
    Args:
        db: Database session
        session_id: ID of the chat session
        
    Returns:
        List of MessageOut Pydantic models
    """
    # Execute query
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    
    # Get all messages and convert to Pydantic models
    messages = result.scalars().all()
    # Convert to MessageOut models which include all required fields
    return [MessageOut.model_validate(msg) for msg in messages]


async def add_document(db: AsyncSession, filename: str, content: str) -> Document:
    doc = Document(filename=filename, content=content)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def list_documents(db: AsyncSession) -> List[DocumentOut]:
    """
    List all documents and return them as Pydantic models.
    """
    result = await db.execute(select(Document))
    documents = result.scalars().all()
    return [DocumentOut.model_validate(doc).model_dump(include=['filename', 'content']) for doc in documents]



