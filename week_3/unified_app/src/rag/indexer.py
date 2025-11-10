import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from src.utils.llm import get_embeddings
from src.utils.text import chunk_text
from pypdf import PdfReader

SUPPORTED_EXT = {".pdf", ".txt", ".md"}

def read_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(path)
        return "\n\n".join([page.extract_text() or "" for page in reader.pages])
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def build_or_update_index(files: List[str], persist_dir: str = ".chroma/voice", embeddings_provider: Optional[str] = None):
    emb = get_embeddings(embeddings_provider)
    os.makedirs(persist_dir, exist_ok=True)

    texts = []
    metadatas = []
    for path in files:
        if os.path.splitext(path)[1].lower() not in SUPPORTED_EXT:
            continue
        raw = read_text(path)
        for chunk in chunk_text(raw, chunk_size=1100, chunk_overlap=120):
            texts.append(chunk)
            metadatas.append({"source": os.path.basename(path)})

    if not texts:
        raise ValueError("No supported documents provided.")

    vect = Chroma.from_texts(texts=texts, embedding=emb, metadatas=metadatas, persist_directory=persist_dir)
    vect.persist()
    return vect