import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-oss-20b:free"
KB_PATH = "knowledge_base"


# Base directory for the knowledge base
BASE_DIR = Path(__file__).parent.parent.parent

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.txt',
    '.md',
    '.pdf',
    '.docx',
    '.csv',
    '.json'
}

# Chunking settings for document processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
