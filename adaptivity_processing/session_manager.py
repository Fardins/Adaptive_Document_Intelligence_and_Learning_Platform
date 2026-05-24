"""
session_manager.py
==================
Quiz session recording and learning analytics manager.

Purpose:
    Saves quiz sessions and updates adaptive learning statistics.

Responsibilities:
    - Store completed quiz sessions
    - Update mastery database
    - Track question correctness
    - Maintain learning history

Workflow:
    Quiz Results
        → Save Session
        → Update Mastery
        → Refresh Analytics

"""

from datetime import datetime

from adaptivity_processing.knowledge_base import (
    save_session,
    update_mastery
)


def record_session(
    section_id,
    results,
    book_name=""
):

    session_data = {
        "timestamp": str(datetime.now()),
        "section_id": section_id,
        "book_name": book_name,
        "results": results
    }

    save_session(session_data)

    for r in results:

        update_mastery(
            section_id=section_id,
            question=r["question"],
            correct=r["correct"],
            book_name=book_name
        )