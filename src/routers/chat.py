from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import SESSION_COOKIE_NAME
from src.database import get_session
from src.database_operations import add_message, create_chat_session, get_chat_session, get_messages
from src.schemas import ChatRequest, ChatResponse
from src.services.chat_service import generate_ai_response

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