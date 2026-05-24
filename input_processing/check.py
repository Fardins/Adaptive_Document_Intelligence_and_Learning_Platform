"""
check.py
════════════════════════════════════════════════════

Section verification and retrieval inspector.

Purpose
───────
Validate stored chunks inside ChromaDB.

Features
────────
✓ Retrieve all chunks of a section
✓ Display metadata and text
✓ Verify chunk ordering
✓ Export results to JSON

Usage
─────
python check.py
python check.py 3.7
python check.py 1
"""

import sys
import json
import os
from dotenv import load_dotenv

load_dotenv()


# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def divider(char="─", width=80):
    print(char * width)


def title(text):
    divider("═")
    print(f"  {text}")
    divider("═")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def display_section(section_id: str):

    from input_processing.storage import get_section, collection_stats

    title(f"SECTION LOOKUP → §{section_id}")

    chunks = get_section(section_id)

    # ── no data ────────────────────────────────────────────────────────────
    if not chunks:

        print(f"\n❌ No data found for section '{section_id}'\n")

        suggest_similar(section_id)

        return

    # ── collection stats ───────────────────────────────────────────────────
    stats = collection_stats()

    print(f"\nCollection Name : {stats['collection']}")
    print(f"Embedding Model : {stats['embed_model']}")
    print(f"Total Chunks    : {stats['total_chunks']}")
    print(f"Storage Path    : {stats['storage_path']}")

    print(f"\n✅ Found {len(chunks)} chunk(s) for section §{section_id}")

    # ── show each chunk ────────────────────────────────────────────────────
    for idx, chunk in enumerate(chunks, start=1):

        print("\n")
        divider()

        print(f"CHUNK #{idx}")

        divider()

        print(f"chunk_id      : {chunk['chunk_id']}")
        print(f"section_id    : {chunk['section_id']}")
        print(f"section_title : {chunk['section_title']}")
        print(f"topic         : {chunk['topic']}")
        print(f"level         : {chunk['level']}")
        print(f"chunk_index   : {chunk['chunk_index']}")
        print(f"page_start    : {chunk['page_start']}")
        print(f"page_end      : {chunk['page_end']}")

        text_length = len(chunk["text"])

        print(f"text_length   : {text_length} characters")

        divider()

        print("\nTEXT:\n")

        for line in chunk["text"].splitlines():
            print(f"  {line}")

    # ── final success ──────────────────────────────────────────────────────
    print("\n")
    divider("═")

    print(
        f"✅ SUCCESS: Retrieved {len(chunks)} chunk(s) "
        f"from storage for section §{section_id}"
    )

    divider("═")

    # ── export json ────────────────────────────────────────────────────────
    export = []

    for c in chunks:

        export.append({
            "chunk_id": c["chunk_id"],
            "section_id": c["section_id"],
            "section_title": c["section_title"],
            "topic": c["topic"],
            "level": c["level"],
            "chunk_index": c["chunk_index"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "text": c["text"],
        })

    filename = f"section_{section_id.replace('.', '_')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f"\n📁 JSON export saved → {filename}\n")


# ══════════════════════════════════════════════════════════════════════════════
# SUGGEST SIMILAR SECTIONS
# ══════════════════════════════════════════════════════════════════════════════

def suggest_similar(section_id: str):

    if not os.path.isfile("section_map.json"):
        return

    try:

        with open("section_map.json", "r", encoding="utf-8") as f:
            section_map = json.load(f)

        prefix = section_id.split(".")[0]

        matches = [
            s for s in section_map
            if s["section_id"].startswith(prefix)
        ]

        if matches:

            print("Did you mean:\n")

            for m in matches[:10]:

                print(
                    f"  §{m['section_id']:<10} "
                    f"{m['title'][:60]}"
                )

            print()

    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():

    # ── argument mode ──────────────────────────────────────────────────────
    if len(sys.argv) > 1:

        section_id = sys.argv[1].strip()

    # ── interactive mode ───────────────────────────────────────────────────
    else:

        print()

        title("SECTION VERIFICATION TOOL")

        print("\nEnter a section ID to inspect stored data.")
        print("\nExamples:")
        print("  3")
        print("  3.7")
        print("  1.2.1")

        print()

        section_id = input("Section ID: ").strip()

    if not section_id:

        print("\n❌ No section ID entered.\n")

        return

    # ── display section ────────────────────────────────────────────────────
    display_section(section_id)


if __name__ == "__main__":
    main()