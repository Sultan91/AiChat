from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
from pathlib import Path
from src.services.kb_service import get_knowledge_base
from src.config import KB_PATH, SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/api/kb", tags=["knowledge-base"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the knowledge base."""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    # Save the file
    file_path = os.path.join(KB_PATH, file.filename)
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Reload documents in the knowledge base
        kb = get_knowledge_base()
        kb.load_documents()
        
        return {"status": "success", "message": f"File {file.filename} uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/documents")
async def list_documents():
    """List all documents in the knowledge base."""
    kb = get_knowledge_base()
    if not kb.documents:
        kb.load_documents()
    
    # Group chunks by source file
    sources = {}
    for doc in kb.documents:
        source = doc.metadata.get('source', 'Unknown')
        if source not in sources:
            sources[source] = {
                'chunks': 0,
                'size': doc.metadata.get('size', 0),
                'last_modified': doc.metadata.get('last_modified', 0)
            }
        sources[source]['chunks'] += 1
    
    return {
        "documents": [
            {
                "source": source,
                "chunks": info['chunks'],
                "size": info['size'],
                "last_modified": info['last_modified']
            }
            for source, info in sources.items()
        ]
    }

@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base."""
    file_path = os.path.join(KB_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Reload documents in the knowledge base
        kb = get_knowledge_base()
        kb.load_documents()
        
        return {"status": "success", "message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.get("/search")
async def search_knowledge_base(query: str, top_k: int = 3):
    """Search the knowledge base for relevant information."""
    kb = get_knowledge_base()
    if not kb.documents:
        kb.load_documents()
    
    results = kb.search(query, top_k=top_k)
    
    return {
        "query": query,
        "results": [
            {
                "content": doc.content,
                "source": doc.metadata.get('source', 'Unknown'),
                "score": float(score)
            }
            for doc, score in results
        ]
    }
