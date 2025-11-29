from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
