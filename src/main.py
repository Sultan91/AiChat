from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
from src.routers.chat import chat_router
from src.routers.kb import kb_router

"""
Prod ready run:
 gunicorn src.main:app  -k uvicorn.workers.UvicornWorker  --workers 4   --bind 0.0.0.0:8000

"""

app = FastAPI()

# Set up static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Include routers
app.include_router(chat_router)
app.include_router(kb_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
