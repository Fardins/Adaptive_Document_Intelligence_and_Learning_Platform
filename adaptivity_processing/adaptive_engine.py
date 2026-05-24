"""
adaptive_engine.py
==================
Adaptive MCQ intelligence engine.

Purpose:
    Builds dynamic prompts for personalized quiz generation.

Features:
    - Detects first-time vs returning learners
    - Adjusts difficulty using mastery score
    - Avoids repeated questions
    - Focuses on weak concepts
    - Encourages conceptual reasoning

Workflow:
    section_id → weakness profile → adaptive prompt → MCQ generator

"""

from adaptivity_processing.knowledge_base import get_weakness_profile


def build_adaptive_prompt(
    section_id,
    chunk_text,
    n_questions
):

    profile = get_weakness_profile(section_id)

    # ──────────────────────────────────────────────────────────────────────
    # FIRST RUN
    # ──────────────────────────────────────────────────────────────────────

    if profile["is_first_time"]:

        return f"""
Generate {n_questions} balanced MCQs from the text.

Focus on:
- foundational understanding
- broad topic coverage

TEXT:
{chunk_text}
"""

    # ──────────────────────────────────────────────────────────────────────
    # RETURNING USER
    # ──────────────────────────────────────────────────────────────────────

    mastery = profile["mastery_score"]

    seen_questions = profile["questions_seen"][-20:]

    return f"""
This user has previously studied this section.

ADAPTIVE LEARNING MODE:

User mastery score:
{mastery:.2f}

IMPORTANT:

1. Focus more on concepts the user may struggle with.
2. Avoid repeating previously asked questions.
3. Generate concept variations instead of duplicates.
4. Increase reasoning difficulty slightly.
5. Emphasize misunderstood concepts.

Previously seen questions:
{seen_questions}

Generate {n_questions} NEW MCQs.

TEXT:
{chunk_text}
"""