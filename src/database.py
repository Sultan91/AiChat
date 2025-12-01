# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Async session factory
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)
# Base ORM class
Base = declarative_base()


# Dependency for FastAPI endpoints
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


