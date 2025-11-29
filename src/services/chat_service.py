from sqlalchemy.orm import Session
from src.models import Session as ChatSession, Message
from src.schemas import MessageOut
from src.services.llm_client import ask_openrouter
from src.services.kb_service import load_kb_documents

def get_or_create_session(db: Session, session_id: str):
    session = db.get(ChatSession, session_id)
    if not session:
        session = ChatSession(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def save_message(db: Session, session_id: str, role: str, content: str):
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()


def generate_ai_response(db: Session, session_id: str, user_message: str):
    # 1. Save user msg
    save_message(db, session_id, "user", user_message)

    # 2. Load conversation history
    msgs = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.timestamp).all()

    messages = [{"role": m.role, "content": m.content} for m in msgs]

    # 3. Append Knowledge Base (simple version)
    kb_text = "\n\n".join(load_kb_documents())
    messages.insert(0, {"role": "system", "content": f"Use this knowledge base:\n{kb_text}"})

    # 4. AI call
    ai_reply = ask_openrouter(messages)

    # 5. Save AI msg
    save_message(db, session_id, "assistant", ai_reply)

    # 6. Return response and full history
    return ai_reply, msgs + [Message(role="assistant", content=ai_reply)]
