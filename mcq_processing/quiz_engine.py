"""
quiz_engine.py
==============
Retrieve content from ChromaDB for quiz generation.

Supports:
  - Section-level retrieval
  - Chunk-level retrieval
  - Combined section reconstruction

Input Formats:
  4.7
      → retrieves all chunks from section 4.7

  4.7::0
      → retrieves a specific chunk

Features:
  - Fetches text + metadata together.
  - Combines multi-chunk sections automatically.
  - Returns structured dictionary output.
  - Compatible with persistent ChromaDB storage.

Public API:
  get_content(user_input)
      → retrieve chunk or section content
"""

from input_processing.storage import _col


def get_content(user_input):
    """
    Accepts:
        4.7
        4.7::0

    Returns:
        combined text
    """

    user_input = user_input.strip()

    # ──────────────────────────────────────────────────────────────────────
    # CASE 1 → chunk_id
    # ──────────────────────────────────────────────────────────────────────

    if "::" in user_input:

        result = _col.get(
            ids=[user_input],
            include=["documents", "metadatas"]
        )

        if not result["ids"]:
            return None

        return {
            "id": user_input,
            "text": result["documents"][0],
            "metadata": result["metadatas"][0]
        }

    # ──────────────────────────────────────────────────────────────────────
    # CASE 2 → section_id
    # ──────────────────────────────────────────────────────────────────────

    result = _col.get(
        where={"section_id": user_input},
        include=["documents", "metadatas"]
    )

    if not result["ids"]:
        return None

    # combine all chunks
    combined_text = "\n\n".join(result["documents"])

    return {
        "id": user_input,
        "text": combined_text,
        "metadata": result["metadatas"][0]
    }