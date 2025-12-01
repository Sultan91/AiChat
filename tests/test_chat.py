# tests/test_chat.py
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.database import get_session, Base
from src.routers.chat import chat_router
from src.constants import SESSION_COOKIE_NAME

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_session():
    async with AsyncSessionLocal() as session:
        yield session

app = FastAPI()
app.include_router(chat_router)
app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_chat_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/chat/", json={"message": "Hello"})
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "session_id" in data
        cookies = response.cookies
        assert SESSION_COOKIE_NAME in cookies
        assert cookies[SESSION_COOKIE_NAME] == data["session_id"]
        return cookies[SESSION_COOKIE_NAME]  # for reuse in other tests

@pytest.mark.asyncio
async def test_get_session_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # Create session first
        resp = await ac.post("/chat/", json={"message": "Hello"})
        session_id = resp.cookies[SESSION_COOKIE_NAME]

        response = await ac.get("/chat/session", cookies={SESSION_COOKIE_NAME: session_id})
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

@pytest.mark.asyncio
async def test_get_chat_history():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # Create session first
        resp = await ac.post("/chat/", json={"message": "Hello"})
        session_id = resp.cookies[SESSION_COOKIE_NAME]

        response = await ac.get(f"/chat/{session_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["role"] == "user"
        assert data[0]["content"] == "Hello"

@pytest.mark.asyncio
async def test_list_chat_sessions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # Create a session
        await ac.post("/chat/", json={"message": "Hi"})
        response = await ac.get("/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "session_id" in data[0]
        assert "created_at" in data[0]

@pytest.mark.asyncio
async def test_delete_chat_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # Create a session
        resp = await ac.post("/chat/", json={"message": "Bye"})
        session_id = resp.cookies[SESSION_COOKIE_NAME]

        # Delete the session
        response = await ac.delete(f"/chat/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Check it was actually deleted
        response = await ac.get(f"/chat/{session_id}/history")
        assert response.status_code == 404
