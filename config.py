"""
config.py
════════════════════════════════════════════════════════════════════
Global configuration settings for the Adaptive Document Preparation
System.

Purpose:
    - Store all reusable project settings in one place
    - Avoid hardcoded values across the codebase
    - Simplify maintenance and future scaling

Includes:
    • PDF document paths
    • Embedding model configuration
    • Vector database settings
    • LLM generation settings
"""

from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Document Processing
# ─────────────────────────────────────────────────────────────────────────────

# Path to your PDF book
PDF_PATH = "./books/SLATEFALL_DOSSIER.pdf"

# HuggingFace embedding model (free, runs locally)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ─────────────────────────────────────────────────────────────────────────────
# ChromaDB Configuration
# ─────────────────────────────────────────────────────────────────────────────

# ChromaDB storage folder
CHROMA_PATH = Path("./chroma_store")

# ChromaDB collection name
CHROMA_COLLECTION = "book_chunks"


# ─────────────────────────────────────────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Groq model for MCQ generation
GROQ_MODEL = "llama-3.1-8b-instant"
