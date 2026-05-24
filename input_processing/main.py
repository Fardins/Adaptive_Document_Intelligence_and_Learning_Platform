"""
main.py
════════════════════════════════════════════════════

Master runner for the PDF → RAG pipeline.

Commands
────────
python main.py
    Run full pipeline

python main.py --stats
    Show ChromaDB stats

python main.py --list
    List stored sections

python main.py --check 3.7
    Verify stored section

Features
────────
✓ Pipeline orchestration
✓ Database inspection
✓ Section verification
✓ Interactive CLI support
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()


def divider(char="═", width=70):
    print(char * width)


def title(text):
    divider()
    print(f"  {text}")
    divider()


def run_pipeline(pdf_path: str):

    if not os.path.isfile(pdf_path):
        print(f"\n❌ File not found: {pdf_path}")
        sys.exit(1)

    title("MASTER PDF INGESTION PIPELINE")

    print(f"\n📘 PDF: {pdf_path}")

    # STEP 1
    print("\n")
    divider("─")
    print(" STEP 1 → PARSING PDF")
    divider("─")

    from input_processing.parser import extract_sections

    sections = extract_sections(pdf_path)

    if not sections:
        print("\n❌ No sections extracted.")
        sys.exit(1)

    # STEP 2
    print("\n")
    divider("─")
    print(" STEP 2 → CHUNKING")
    divider("─")

    from input_processing.chunker import chunk_sections

    chunks = chunk_sections(sections)

    if not chunks:
        print("\n❌ No chunks produced.")
        sys.exit(1)

    # STEP 3
    print("\n")
    divider("─")
    print(" STEP 3 → EMBEDDING + STORAGE")
    divider("─")

    from input_processing.storage import store_chunks, collection_stats

    store_chunks(chunks)

    stats = collection_stats()

    # SAVE SECTION MAP
    section_map = [
        {
            "section_id": s["section_id"],
            "title": s["section_title"],
            "level": s["level"],
            "page_start": s["page_start"],
            "page_end": s["page_end"],
        }
        for s in sections
    ]

    with open("section_map.json", "w", encoding="utf-8") as f:
        json.dump(section_map, f, indent=2, ensure_ascii=False)

    # FINAL
    print("\n")
    title("PIPELINE COMPLETE")

    print(f"\nSections Extracted : {len(sections)}")
    print(f"Chunks Stored      : {stats['total_chunks']}")
    print(f"Embedding Model    : {stats['embed_model']}")
    print(f"Chroma Collection  : {stats['collection']}")
    print(f"Storage Path       : {stats['storage_path']}")

    print("\n📚 Sections:")
    for sec in sections:
        print(
            f"  §{sec['section_id']:<10} "
            f"{sec['section_title'][:60]}"
        )

    print("\n✅ All pipeline stages completed successfully.\n")


def show_stats():
    from input_processing.storage import collection_stats

    stats = collection_stats()

    title("CHROMADB STATS")

    for k, v in stats.items():
        print(f"{k:<18}: {v}")


def list_sections():
    from input_processing.storage import _col

    title("ALL STORED SECTIONS")

    total = _col.count()

    if total == 0:
        print("\nDatabase is empty.\n")
        return

    result = _col.get(include=["metadatas"], limit=total)

    seen = {}

    for meta in result["metadatas"]:
        sid = meta.get("section_id")

        if sid not in seen:
            seen[sid] = meta.get("section_title")

    def sort_key(x):
        try:
            return [int(i) for i in x.split(".")]
        except:
            return [0]

    for sid in sorted(seen.keys(), key=sort_key):
        print(f"§{sid:<10} {seen[sid]}")


def main():

    if "--stats" in sys.argv:
        show_stats()
        return

    if "--list" in sys.argv:
        list_sections()
        return

    if "--check" in sys.argv:
        idx = sys.argv.index("--check")

        if idx + 1 >= len(sys.argv):
            print("Missing section ID")
            return

        from input_processing.check import display_section

        display_section(sys.argv[idx + 1])
        return

    pdf_path = None

    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            pdf_path = arg
            break

    if not pdf_path:
        pdf_path = os.getenv("PDF_PATH", "")

    if not pdf_path:
        pdf_path = input("Enter PDF path: ").strip()

    run_pipeline(pdf_path)


if __name__ == "__main__":
    main()