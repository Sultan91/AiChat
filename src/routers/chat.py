from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.schemas import ChatRequest, ChatResponse
from src.services.chat_service import get_or_create_session, generate_ai_response

chat_router = APIRouter(prefix="/chat")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@chat_router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    get_or_create_session(db, req.session_id)

    reply, history = generate_ai_response(db, req.session_id, req.message)

    return ChatResponse(
        reply=reply,
        history=history
    )