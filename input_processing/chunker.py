"""
chunker.py 
========== 
Splits each section's text into smaller chunks. 
Rules: 
  ✓ Each section is chunked INDEPENDENTLY — text never crosses section boundary. 
  ✓ Splits on: paragraph → sentence → word (graceful degradation) 
  ✓ Sections shorter than CHUNK_SIZE are stored as a single chunk. 
  
Each chunk carries this metadata: 
   { "section_id": str, e.g. "3.7" 
     "section_title": str, 
     "topic": str, same as section_title 
     "level": int, 
     "chunk_id": str, e.g. "3.7::0", "3.7::1" 
     "chunk_index": int, 0-based within the section 
     "page_start": int, 
     "page_end": int, 
     "text": str } 
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 120

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_sections(sections):

    all_chunks = []

    for sec in sections:

        text = sec["raw_text"].strip()

        if not text:
            continue

        pieces = (
            [text]
            if len(text) <= CHUNK_SIZE
            else splitter.split_text(text)
        )

        for idx, piece in enumerate(pieces):

            all_chunks.append({
                "section_id": sec["section_id"],
                "section_title": sec["section_title"],
                "topic": sec["section_title"],
                "level": sec["level"],
                "chunk_id": f"{sec['section_id']}::{idx}",
                "chunk_index": idx,
                "page_start": sec["page_start"],
                "page_end": sec["page_end"],
                "text": piece.strip(),
            })

        print(
            f"[chunker] §{sec['section_id']} "
            f"→ {len(pieces)} chunk(s)"
        )

    print(f"\n[chunker] ✓ {len(all_chunks)} total chunks")

    return all_chunks