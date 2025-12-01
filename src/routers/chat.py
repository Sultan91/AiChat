from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Response, status
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from src.constants import SESSION_COOKIE_NAME
from src.database import get_session
from src.database_operations import add_message, create_chat_session, get_chat_session, get_messages, get_all_chat_sessions
from src.models import Message
from src.schemas import ChatRequest, ChatResponse, ChatSessionOut
from src.services.chat_service import generate_ai_response

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
chat_router = APIRouter(prefix="/chat")



@chat_router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest,
               request: Request,
               response: Response,
               db: AsyncSession = Depends(get_session)):
    # Create or load session
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        # Create new session
        session_id = str(uuid4())
        # Set HttpOnly cookie
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=True,        # recommended in production
            samesite="Lax",
            path="/",
            max_age=60*60*24*30 # 30 days
        )
        chat_session = await create_chat_session(db, session_id)
    else:
        # Continue with existing chat session
        chat_session = await get_chat_session(db, session_id)
        if not chat_session:
            chat_session = await create_chat_session(db, session_id)
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                httponly=True,
                secure=True,
                samesite="Lax",
                path="/",
            )


    # # fetch previous messages
    history = await get_messages(db, chat_session.id)
    history_dicts = [msg.model_dump() for msg in history]

    agent_reply = await generate_ai_response(db, chat_session.id, req.message)
    await add_message(db, chat_session.id, "assistant", agent_reply)

    # Convert MessageOut objects to dictionaries before returning

    return ChatResponse(
        reply=str(agent_reply),
        session_id=chat_session.session_id,
        history=history_dicts
    )


@chat_router.get("/{session_id}/history")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Retrieve message history for a specific chat session.
    
    Args:
        session_id: The ID of the chat session
        
    Returns:
        List of messages in the chat history
    """
    # Get the chat session
    chat_session = await get_chat_session(db, session_id)
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get messages for the session
    messages = await get_messages(db, chat_session.id)
    
    # Convert messages to dictionaries
    return [msg.model_dump() for msg in messages]


@chat_router.get("/sessions")
async def list_chat_sessions(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """List all chat sessions"""
    sessions = await get_all_chat_sessions(db)
    return [
        {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat() if session.created_at else None
        }
        for session in sessions
    ]


@chat_router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_session)
):
    """Delete a chat session and all its messages"""
    session = await get_chat_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Delete messages first due to foreign key constraint
    await db.execute(
        delete(Message).where(Message.session_id == session.id)
    )
    # Then delete the session
    await db.delete(session)
    await db.commit()
    
    return {"status": "success", "message": "Session deleted successfully"}


@chat_router.get("/sessions/page")
async def view_chat_sessions(request: Request):
    """Render the chat sessions page"""
    return templates.TemplateResponse("sessions.html", {"request": request})


@chat_router.get("/session")
async def get_session_id(request: Request):
    """Get the current session ID from cookies"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )
    return {"session_id": session_id}


@chat_router.get("/history")
async def view_chat_history(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_session)
):
    """Render the chat history page"""
    # Verify session exists
    chat_session = await get_chat_session(db, session_id)
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "session_id": session_id
        }
    )

