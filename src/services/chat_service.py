from typing import List, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import Message
from src.schemas import MessageOut
from src.services.llm_client import ask_openrouter
from src.services.kb_service import get_knowledge_base

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context. 

INSTRUCTIONS:
1. The following context is the most relevant information from our knowledge base that directly relates to the user's question.
2. You MUST prioritize this information when formulating your response.
3. If the context contains the answer, provide a clear and concise response based on it.
4. If the context is relevant but doesn't fully answer the question, use it as a basis and supplement with your general knowledge.
5. If the context is not relevant to the question, you may use your general knowledge.
6. Always be accurate and factual. If you're uncertain, say so.

CONTEXT:
{context}

USER QUESTION: {question}

YOUR RESPONSE (based on the context above):"""



async def save_message(db: AsyncSession, session_id: int, role: str, content: str) -> Message:
    """Save a message to the database."""
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_messages(db: AsyncSession, session_id: int) -> List[MessageOut]:
    """Get all messages for a session."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [MessageOut.model_validate(msg) for msg in messages]


def get_knowledge_context(question: str, top_k: int = 3) -> str:
    """Get relevant context from the knowledge base for the given question."""
    kb = get_knowledge_base()
    if not kb.documents:
        kb.load_documents()
    return kb.get_relevant_context(question, top_k=top_k)


async def generate_ai_response(
    db: AsyncSession,
    session_id: int,
    user_message: str,
    use_knowledge_base: bool = True
) -> tuple[str, List[MessageOut]]:
    """
    Generate an AI response to a user message, optionally using the knowledge base.
    
    Args:
        db: Database session
        session_id: ID of the chat session
        user_message: The user's message
        use_knowledge_base: Whether to use the knowledge base for context
        
    Returns:
        A tuple of (ai_reply, message_history)
    """
    # 1. Save user message
    await save_message(db, session_id, "user", user_message)
    
    # 2. Get conversation history
    messages = await get_messages(db, session_id)
    
    # 3. Prepare messages for the LLM
    message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # 4. Get relevant context from knowledge base if enabled
    if use_knowledge_base:
        context = get_knowledge_context(user_message, 10)
        if context:
            system_prompt = SYSTEM_PROMPT.format(
                context=context,
                question=user_message
            )
            # Insert system prompt at the beginning
            message_dicts.insert(0, {"role": "assistant", "content": system_prompt})
    
    # 5. Call the LLM
    ai_reply = ask_openrouter(message_dicts)
    
    # 6. Save AI response
    await save_message(db, session_id, "assistant", ai_reply)
    
    # 7. Return the response and updated message history
    return ai_reply
