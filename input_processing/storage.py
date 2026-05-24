""" 
storage.py 
========== 
Embeds chunks with a HuggingFace model (token from .env) and stores them in a persistent ChromaDB collection. 

Embedding: 
  - Model loaded via sentence-transformers, authenticated with HF_TOKEN. 
  - Default model: sentence-transformers/all-MiniLM-L6-v2 (384-dim, free). 
Storage: 
  - ChromaDB with cosine similarity. 
  - Persistent on disk at CHROMA_PATH. 
  - Upsert-safe: re-running ingestion won't create duplicates. 
  
Public API: store_chunks(chunks) 
          → embed + upsert all chunks get_section(section_id) 
          → all chunks of one section, ordered query(text, n, section_ids) 
          → semantic search collection_stats() 
          → print DB summary clear() 
          → wipe collection 
"""

import os
import chromadb

from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from config import EMBEDDING_MODEL, CHROMA_PATH, CHROMA_COLLECTION

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")

EMBED_MODEL = EMBEDDING_MODEL
COLLECTION_NAME = CHROMA_COLLECTION

print(f"[storage] Loading model: {EMBED_MODEL}")

model_kwargs = {}

if HF_TOKEN:
    model_kwargs["token"] = HF_TOKEN

embed_model = SentenceTransformer(
    EMBED_MODEL,
    **model_kwargs
)

print("[storage] Model ready ✓")

os.makedirs(CHROMA_PATH, exist_ok=True)

client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False)
)

_col = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

print("[storage] ChromaDB ready ✓")


def embed(texts):

    return embed_model.encode(
        texts,
        show_progress_bar=False
    ).tolist()


def store_chunks(chunks):

    ids = [c["chunk_id"] for c in chunks]

    docs = [c["text"] for c in chunks]

    metas = []

    for c in chunks:

        metas.append({
            "section_id": c["section_id"],
            "section_title": c["section_title"],
            "topic": c["topic"],
            "level": c["level"],
            "chunk_index": c["chunk_index"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
        })

    print(f"[storage] Embedding {len(chunks)} chunks...")

    vectors = embed(docs)

    _col.upsert(
        ids=ids,
        documents=docs,
        embeddings=vectors,
        metadatas=metas,
    )

    print("[storage] ✓ Stored successfully")


def get_section(section_id):

    res = _col.get(
        where={"section_id": str(section_id)},
        include=["documents", "metadatas"]
    )

    if not res["ids"]:
        return []

    chunks = []

    for i, cid in enumerate(res["ids"]):

        meta = res["metadatas"][i]

        chunks.append({
            "chunk_id": cid,
            "section_id": meta["section_id"],
            "section_title": meta["section_title"],
            "topic": meta["topic"],
            "level": meta["level"],
            "chunk_index": meta["chunk_index"],
            "page_start": meta["page_start"],
            "page_end": meta["page_end"],
            "text": res["documents"][i],
        })

    chunks.sort(key=lambda x: x["chunk_index"])

    return chunks


def collection_stats():

    return {
        "collection": COLLECTION_NAME,
        "total_chunks": _col.count(),
        "storage_path": CHROMA_PATH,
        "embed_model": EMBED_MODEL,
    }