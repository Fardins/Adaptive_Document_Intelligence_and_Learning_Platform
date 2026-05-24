"""
parser.py
════════════════════════════════════════════════════

Structured PDF section parser.

Features
────────
✓ Extracts real section IDs from headings
✓ Supports nested sections (1, 1.2, 1.2.3)
✓ Preserves page ranges
✓ Prevents section bleed

Example
───────
Input:
    3.2 Transformer Architecture

Output:
    section_id    = "3.2"
    section_title = "Transformer Architecture"

Public API
──────────
extract_sections(pdf_path)
    Parse PDF into structured sections
"""

try:
    import fitz
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "PyMuPDF is required for PDF parsing. Install it with: pip install pymupdf"
    ) from exc

import statistics
import re
import os


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_body_font_size(doc):

    sizes = []

    for page in doc:

        blocks = page.get_text("dict")["blocks"]

        for block in blocks:

            if block.get("type") != 0:
                continue

            for line in block["lines"]:

                for span in line["spans"]:

                    text = span["text"].strip()

                    if text and len(text) > 3:
                        sizes.append(span["size"])

    return statistics.median(sizes) if sizes else 11.0


def is_noise(text):

    text = text.strip()

    if not text:
        return True

    if re.fullmatch(r"\d{1,5}", text):
        return True

    if re.fullmatch(r"https?://\S+", text):
        return True

    return False


def extract_section_info(text):
    """
    Extract REAL section ID from heading.

    Example:
        "3.2 Transformer Architecture"

    Returns:
        ("3.2", "Transformer Architecture")
    """

    text = text.strip()

    pattern = r"^(\d+(?:\.\d+)*)\s+(.*)$"

    match = re.match(pattern, text)

    if match:

        section_id = match.group(1).strip()

        title = match.group(2).strip()

        return section_id, title

    return None, text


def detect_level(section_id):

    return len(section_id.split("."))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PARSER
# ══════════════════════════════════════════════════════════════════════════════

def extract_sections(pdf_path):

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)

    total_pages = len(doc)

    body_size = get_body_font_size(doc)

    threshold = body_size * 1.12

    print(
        f"\n[parser] PDF:"
        f" {os.path.basename(pdf_path)}"
        f" | pages={total_pages}"
        f" | body_font≈{body_size:.1f}"
    )

    sections = []

    current = None

    # ──────────────────────────────────────────────────────────────────────
    # WALK THROUGH PDF
    # ──────────────────────────────────────────────────────────────────────

    for page_num, page in enumerate(doc, start=1):

        blocks = page.get_text("dict")["blocks"]

        for block in blocks:

            if block.get("type") != 0:
                continue

            for line in block["lines"]:

                text = "".join(
                    span["text"]
                    for span in line["spans"]
                ).strip()

                if not text:
                    continue

                dominant = max(
                    line["spans"],
                    key=lambda s: s["size"]
                )

                font_size = dominant["size"]

                is_heading = (
                    font_size >= threshold
                    and len(text) <= 250
                    and not is_noise(text)
                )

                # ──────────────────────────────────────────────────────────
                # HEADING
                # ──────────────────────────────────────────────────────────

                if is_heading:

                    section_id, clean_title = extract_section_info(text)

                    # skip headings without numeric section IDs
                    if not section_id:
                        continue

                    # close previous section
                    if current:

                        current["raw_text"] = (
                            current["raw_text"].strip()
                        )

                        if current["raw_text"]:
                            sections.append(current)

                    level = detect_level(section_id)

                    current = {
                        "section_id": section_id,
                        "section_title": clean_title,
                        "level": level,
                        "page_start": page_num,
                        "page_end": page_num,
                        "raw_text": "",
                    }

                # ──────────────────────────────────────────────────────────
                # NORMAL TEXT
                # ──────────────────────────────────────────────────────────

                else:

                    if current is None:

                        current = {
                            "section_id": "0",
                            "section_title": "Preamble",
                            "level": 0,
                            "page_start": page_num,
                            "page_end": page_num,
                            "raw_text": "",
                        }

                    current["raw_text"] += text + "\n"

                    current["page_end"] = page_num

    # ──────────────────────────────────────────────────────────────────────
    # FINAL SECTION
    # ──────────────────────────────────────────────────────────────────────

    if current:

        current["raw_text"] = current["raw_text"].strip()

        if current["raw_text"]:
            sections.append(current)

    doc.close()

    # ──────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ──────────────────────────────────────────────────────────────────────

    print(f"\n[parser] ✓ {len(sections)} sections extracted\n")

    for sec in sections:

        words = len(sec["raw_text"].split())

        print(
            f"  §{sec['section_id']:<10}"
            f" p.{sec['page_start']:<3}-{sec['page_end']:<3}"
            f" {words:>6} words"
            f" → {sec['section_title'][:55]}"
        )

    return sections


# ══════════════════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else ""

    if not path:

        print("\nUsage:")
        print("  python parser.py mybook.pdf\n")

        exit()

    sections = extract_sections(path)

    print(f"\nTotal sections: {len(sections)}")