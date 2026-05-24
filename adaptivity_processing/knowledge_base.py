"""
knowledge_base.py
=================
Persistent adaptive learning knowledge base.

Purpose:
    Stores user quiz history and learning mastery analytics.

Tracks:
    - Correct vs wrong answers
    - Question history
    - Section-level mastery
    - Weakness profiles
    - Book metadata

Storage:
    history/quiz_history.json
        → complete session history

    history/mastery.json
        → learning analytics database

Features:
    - Persistent learning memory
    - Weakness analysis
    - Mastery score calculation
    - Duplicate question prevention
    - Multi-book support

"""

import json
import os
from datetime import datetime

HISTORY_DIR = "history"

QUIZ_HISTORY_FILE = os.path.join(
    HISTORY_DIR,
    "quiz_history.json"
)

MASTERY_FILE = os.path.join(
    HISTORY_DIR,
    "mastery.json"
)


# ══════════════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════════════

os.makedirs(HISTORY_DIR, exist_ok=True)

if not os.path.isfile(QUIZ_HISTORY_FILE):

    with open(QUIZ_HISTORY_FILE, "w") as f:
        json.dump([], f)

if not os.path.isfile(MASTERY_FILE):

    with open(MASTERY_FILE, "w") as f:
        json.dump({}, f)


# ══════════════════════════════════════════════════════════════════════════════
# LOADERS
# ══════════════════════════════════════════════════════════════════════════════

def load_history():

    with open(QUIZ_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_mastery():

    with open(MASTERY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════

def save_session(session_data):

    history = load_history()

    history.append(session_data)

    with open(QUIZ_HISTORY_FILE, "w", encoding="utf-8") as f:

        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE MASTERY
# ══════════════════════════════════════════════════════════════════════════════

def update_mastery(section_id, question, correct, book_name=""):

    mastery = load_mastery()

    # always try to read book_name from disk if not passed
    if not book_name:
        try:
            meta_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                ),
                "book_meta.json"
            )
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    book_name = json.load(f).get("book_name", "Unknown")
        except Exception:
            book_name = "Unknown"

    if section_id not in mastery:
        mastery[section_id] = {
            "book_name": book_name,
            "correct": 0,
            "wrong": 0,
            "questions_seen": []
        }

    entry = mastery[section_id]

    # always overwrite book_name to keep it fresh
    if book_name and book_name != "Unknown":
        entry["book_name"] = book_name

    if correct:
        entry["correct"] += 1
    else:
        entry["wrong"] += 1

    entry["questions_seen"].append(question)

    with open(MASTERY_FILE, "w", encoding="utf-8") as f:
        json.dump(mastery, f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

def get_weakness_profile(section_id):

    mastery = load_mastery()

    if section_id not in mastery:

        return {
            "is_first_time": True,
            "weakness_score": 0,
            "mastery_score": 0,
            "questions_seen": []
        }

    data = mastery[section_id]

    correct = data["correct"]
    wrong = data["wrong"]

    total = correct + wrong

    mastery_score = (
        correct / total
        if total > 0 else 0
    )

    weakness_score = (
        wrong / total
        if total > 0 else 0
    )

    return {
        "is_first_time": False,
        "weakness_score": weakness_score,
        "mastery_score": mastery_score,
        "questions_seen": data["questions_seen"]
    }