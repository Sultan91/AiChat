import os
from src.config import KB_PATH

def load_kb_documents():
    docs = []
    for file in os.listdir(KB_PATH):
        if file.endswith(".txt"):
            path = os.path.join(KB_PATH, file)
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs
