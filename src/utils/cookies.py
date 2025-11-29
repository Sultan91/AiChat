from fastapi import Response
import uuid

def create_session_cookie(response: Response):
    session_id = str(uuid.uuid4())
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,        # set True in production behind HTTPS
        samesite="lax",
        max_age=60*60*24*30,  # 30 days
        path="/"
    )
    return session_id