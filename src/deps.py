from fastapi import Cookie, Depends, Response
from src.utils.cookies import create_session_cookie
from src.db import SessionLocal
from src.services.chat_service import get_or_create_session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session_id(
    response: Response,
    session_id: str | None = Cookie(default=None)
):
    """
    Extracts the cookie. If missing, creates a new session cookie.
    """
    if session_id is None:
        session_id = create_session_cookie(response)

    return session_id
