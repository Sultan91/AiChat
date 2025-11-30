import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from numpy.linalg import norm
from src.config import KB_PATH, SUPPORTED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP

class Document:
    def __init__(self, content: str, metadata: Optional[dict] = None):
        self.content = content
        self.metadata = metadata or {}

class KnowledgeBase:
    def __init__(self):
        self.documents: List[Document] = []
        self.embeddings: List[np.ndarray] = []
        self.document_metadata: List[dict] = []
        
    def _get_file_hash(self, file_path: str) -> str:
        """Generate a hash for file content to detect changes."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def _chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []
            
        words = text.split()
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + chunk_size
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start = end - overlap
            
            # Prevent infinite loop with very small chunks
            if end >= len(words):
                break
                
        return chunks
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate a simple embedding for the text (placeholder - replace with actual embedding model)."""
        # This is a simple placeholder - in practice, you'd use a pre-trained model
        # like OpenAI's text-embedding-ada-002 or similar
        words = text.lower().split()
        unique_words = list(set(words))
        embedding = np.zeros(100)  # Simple fixed-size embedding
        for i, word in enumerate(unique_words[:100]):
            embedding[i % 100] = hash(word) % 100 / 100.0  # Simple hash-based embedding
        return embedding / (norm(embedding) + 1e-9)  # Normalize
    
    def load_documents(self, directory: str = None) -> List[Document]:
        """Load and process all supported documents from the knowledge base directory."""
        if directory is None:
            directory = KB_PATH
            
        self.documents = []
        self.document_metadata = []
        
        for file_path in Path(directory).rglob('*'):
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_hash = self._get_file_hash(str(file_path))
                        
                        # Create document metadata
                        metadata = {
                            'source': str(file_path),
                            'hash': file_hash,
                            'size': os.path.getsize(file_path),
                            'last_modified': os.path.getmtime(file_path)
                        }
                        
                        # Split into chunks and create documents
                        chunks = self._chunk_text(content)
                        for i, chunk in enumerate(chunks):
                            chunk_metadata = metadata.copy()
                            chunk_metadata['chunk'] = i
                            self.documents.append(Document(chunk, chunk_metadata))
                            self.document_metadata.append(chunk_metadata)
                            
                except Exception as e:
                    print(f"Error loading {file_path}: {str(e)}")
                    continue
                    
        # Generate embeddings for all documents
        self.embeddings = [self._get_embedding(doc.content) for doc in self.documents]
        return self.documents
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """Search for relevant documents based on the query."""
        if not self.documents:
            return []
            
        query_embedding = self._get_embedding(query)
        similarities = []
        
        for doc_embedding in self.embeddings:
            # Calculate cosine similarity
            sim = np.dot(query_embedding, doc_embedding) / (
                norm(query_embedding) * norm(doc_embedding) + 1e-9
            )
            similarities.append(sim)
            
        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(self.documents[i], similarities[i]) for i in top_indices]
    
    def get_relevant_context(self, query: str, top_k: int = 1) -> str:
        """
        Get the most relevant context from knowledge base for a given query.
        Focuses on the top result and includes it in the system prompt.
        """
        results = self.search(query, top_k=top_k)
        if not results:
            return ""
            
        # Get the top result
        #top_doc, score = results[0]
        docs_merged_context = "\n\n".join([doc.content for doc, _ in results])
        # Format the context to emphasize this is the most relevant information
        context = (
            "IMPORTANT: The following is the most relevant information from the knowledge base:\n"
            # f"SOURCE: {top_doc.metadata.get('source', 'Unknown')}\n"
            f"CONTENT: {docs_merged_context}\n\n"
            "Use this information to provide an accurate and detailed response. "
            "If the information is relevant to the user's question, make sure to reference it in your answer."
        )
        
        return context

# Global knowledge base instance
knowledge_base = KnowledgeBase()

def get_knowledge_base() -> KnowledgeBase:
    """Get the global knowledge base instance."""
    return knowledge_base

def load_kb_documents() -> List[str]:
    """Legacy function for backward compatibility."""
    kb = get_knowledge_base()
    kb.load_documents()
    return [doc.content for doc in kb.documents]
