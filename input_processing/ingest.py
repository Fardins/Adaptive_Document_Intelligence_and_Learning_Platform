"""
ingest.py
════════════════════════════════════════════════════

End-to-end PDF ingestion pipeline.

Workflow
────────
PDF
  ↓
Parse Sections
  ↓
Chunk Text
  ↓
Generate Embeddings
  ↓
Store in ChromaDB

Features
────────
✓ Full ingestion pipeline
✓ Persistent vector storage
✓ Section map export
✓ Safe re-ingestion

Usage
─────
python ingest.py
python ingest.py mybook.pdf
"""

import os
import sys
import json
from dotenv import load_dotenv
from config import PDF_PATH

load_dotenv()


def run(pdf_path: str):
    # ── validate ───────────────────────────────────────────────────────────────
    if not os.path.isfile(pdf_path):
        print(f"\n  ERROR: File not found → {pdf_path}")
        print("  Update PDF_PATH in config.py or pass the path as argument.")
        sys.exit(1)

    print("=" * 60)
    print(f"  INGESTION PIPELINE")
    print(f"  Book : {pdf_path}")
    print("=" * 60)

    # ── step 1: parse ──────────────────────────────────────────────────────────
    print("\n── STEP 1: Parse PDF ─────────────────────────────────────────")
    from input_processing.parser import extract_sections
    sections = extract_sections(pdf_path)

    if not sections:
        print("ERROR: No sections extracted. Check your PDF.")
        sys.exit(1)

    # ── step 2: chunk ──────────────────────────────────────────────────────────
    print("\n── STEP 2: Chunk Sections ────────────────────────────────────")
    from input_processing.chunker import chunk_sections
    chunks = chunk_sections(sections)

    if not chunks:
        print("ERROR: No chunks produced.")
        sys.exit(1)

    # ── step 3: store ──────────────────────────────────────────────────────────
    print("\n── STEP 3: Embed + Store in ChromaDB ────────────────────────")
    from input_processing.storage import store_chunks, collection_stats
    store_chunks(chunks)

    # ── summary ────────────────────────────────────────────────────────────────
    stats = collection_stats()

    print("\n" + "=" * 60)
    print("  INGESTION COMPLETE")
    print("=" * 60)
    print(f"  Sections extracted : {len(sections)}")
    print(f"  Chunks stored      : {stats['total_chunks']}")
    print(f"  Storage path       : {stats['storage_path']}")
    print(f"  Embedding model    : {stats['embed_model']}")
    print()
    print("  Section IDs in this book:")
    for s in sections:
        print(f"    §{s['section_id']:<10}  {s['section_title'][:55]}")

    # Save section map to JSON for reference
    section_map = [
        {"section_id": s["section_id"], "title": s["section_title"],
         "level": s["level"], "pages": f"{s['page_start']}-{s['page_end']}"}
        for s in sections
    ]
    with open("section_map.json", "w", encoding="utf-8") as f:
        json.dump(section_map, f, indent=2, ensure_ascii=False)

    print(f"\n  Section map saved → section_map.json")
    print(f"\n  Next: python check.py")


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else PDF_PATH
    if not pdf_path:
        print("Usage: python ingest.py <path_to_pdf>")
        print("   or: update PDF_PATH in config.py")
        sys.exit(1)
    run(pdf_path)