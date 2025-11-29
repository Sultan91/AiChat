from fastapi import FastAPI
import uvicorn
from src.routers.chat import chat_router
from src.routers.kb import kb_router

"""
Prod ready run:
 gunicorn src.main:app  -k uvicorn.workers.UvicornWorker  --workers 4   --bind 0.0.0.0:8000

"""

app = FastAPI()

app.include_router(chat_router)
app.include_router(kb_router)

