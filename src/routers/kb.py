from fastapi import APIRouter
from src.services.kb_service import load_kb_documents

kb_router = APIRouter(prefix="/kb")

@kb_router.get("/")
def get_kb():
    return {"documents": load_kb_documents()}
