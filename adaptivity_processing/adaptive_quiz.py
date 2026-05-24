"""
adaptive_quiz.py
================
Adaptive MCQ quiz generation and evaluation pipeline.

Purpose:
    Generates intelligent MCQs from section content and evaluates user performance.

Core Features:
    - Adaptive question generation
    - Safe JSON parsing from LLM output
    - Automatic MCQ normalization
    - Retry-safe generation pipeline
    - Interactive quiz system
    - Session tracking + mastery analytics

Pipeline:
    Section Content
        → Adaptive Prompt
        → LLM MCQ Generation
        → JSON Validation
        → Quiz Interaction
        → Knowledge Tracking

"""

import json
import os
import re
import time

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcq_processing.quiz_engine import get_content
from adaptivity_processing.adaptive_engine import build_adaptive_prompt
from adaptivity_processing.session_manager import record_session
from config import GROQ_MODEL

from mcq_processing.mcq_generator import client


# ══════════════════════════════════════════════════════════════════════════════
# SAFE JSON PARSER
# ══════════════════════════════════════════════════════════════════════════════

def extract_json(text):
    """
    Extract JSON array safely from LLM output.
    """

    # remove markdown
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    # try direct parse
    try:
        return json.loads(text)

    except Exception:
        pass

    # try extracting array
    match = re.search(r"\[.*\]", text, re.DOTALL)

    if match:

        json_text = match.group(0)

        return json.loads(json_text)

    raise ValueError("No valid JSON found")


# ══════════════════════════════════════════════════════════════════════════════
# GENERATE MCQS
# ══════════════════════════════════════════════════════════════════════════════

def normalize_options(options):
    """
    Convert list-style options into dict-style options.
    """

    # already correct
    if isinstance(options, dict):
        return options

    # convert list → dict
    if isinstance(options, list):

        labels = ["A", "B", "C", "D"]

        clean = {}

        for idx, item in enumerate(options):

            if idx >= 4:
                break

            text = str(item).strip()

            # remove leading "A." etc
            text = re.sub(
                r"^[A-D][\.\)\:\-]\s*",
                "",
                text
            )

            clean[labels[idx]] = text

        return clean

    return {}


def generate_adaptive_mcqs(
    section_id,
    text,
    n_questions,
    retries=3
):

    prompt = build_adaptive_prompt(
        section_id=section_id,
        chunk_text=text,
        n_questions=n_questions
    )

    prompt += """

IMPORTANT:
Return ONLY valid JSON.

STRICT FORMAT:

[
  {
    "question": "...",
    "options": {
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    },
    "correct_answer": "A",
    "explanation": "..."
  }
]

Do NOT use list format for options.
"""

    for attempt in range(retries):

        try:

            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            mcqs = extract_json(content)

            if not isinstance(mcqs, list):
                raise ValueError("Response is not list")

            # ──────────────────────────────────────────────────────────
            # NORMALIZE MCQS
            # ──────────────────────────────────────────────────────────

            normalized = []

            for mcq in mcqs:

                if "question" not in mcq:
                    continue

                if "options" not in mcq:
                    continue

                options = normalize_options(
                    mcq["options"]
                )

                if len(options) != 4:
                    continue

                correct = str(
                    mcq.get(
                        "correct_answer",
                        "A"
                    )
                ).strip().upper()

                explanation = str(
                    mcq.get(
                        "explanation",
                        ""
                    )
                ).strip()

                normalized.append({
                    "question": mcq["question"].strip(),
                    "options": options,
                    "correct_answer": correct,
                    "explanation": explanation
                })

            if not normalized:
                raise ValueError(
                    "No valid MCQs parsed"
                )

            return normalized

        except Exception as e:

            print(
                f"\n⚠ Parse failed"
                f" ({attempt+1}/{retries})"
            )

            if attempt == retries - 1:

                print("\n❌ RAW OUTPUT:\n")
                if 'content' in locals():
                    print(content)
                else:
                    print(f"API Error: {str(e)}")

                raise e

            time.sleep(1)

    return []


# ══════════════════════════════════════════════════════════════════════════════
# QUIZ
# ══════════════════════════════════════════════════════════════════════════════

def run_adaptive_quiz():

    print()

    section_id = input(
        "Enter section_id: "
    ).strip()

    n_questions = int(
        input("Number of MCQs: ").strip()
    )

    content = get_content(section_id)

    if not content:

        print("\n❌ Section not found")
        return

    text = content["text"]

    print("\nGenerating adaptive quiz...\n")

    mcqs = generate_adaptive_mcqs(
        section_id=section_id,
        text=text,
        n_questions=n_questions
    )

    if not mcqs:

        print("\n❌ Failed to generate MCQs")
        return

    score = 0

    results = []

    # ──────────────────────────────────────────────────────────────────────
    # QUIZ LOOP
    # ──────────────────────────────────────────────────────────────────────

    for idx, mcq in enumerate(mcqs, start=1):

        print("\n" + "─" * 60)

        print(f"\nQ{idx}. {mcq['question']}\n")

        for k, v in mcq["options"].items():

            print(f"  {k}. {v}")

        # user answer
        while True:

            ans = input(
                "\nYour Answer (A/B/C/D): "
            ).strip().upper()

            if ans in ["A", "B", "C", "D"]:
                break

            print("Invalid input.")

        correct_answer = mcq["correct_answer"].upper()

        correct = ans == correct_answer

        # ──────────────────────────────────────────────────────────────
        # CORRECT
        # ──────────────────────────────────────────────────────────────

        if correct:

            print("\n✅ Correct")

            score += 1

        # ──────────────────────────────────────────────────────────────
        # WRONG
        # ──────────────────────────────────────────────────────────────

        else:

            print("\n❌ Wrong")

            print(
                f"\nCorrect Answer:"
                f" {correct_answer}"
            )

            print(
                f"\nExplanation:"
                f"\n{mcq['explanation']}"
            )

        results.append({
            "question": mcq["question"],
            "correct": correct
        })

    # ──────────────────────────────────────────────────────────────────────
    # SAVE SESSION
    # ──────────────────────────────────────────────────────────────────────

    record_session(
        section_id=section_id,
        results=results
    )

    # ──────────────────────────────────────────────────────────────────────
    # FINAL SCORE
    # ──────────────────────────────────────────────────────────────────────

    print("\n")
    print("=" * 60)

    print("\nQUIZ COMPLETE")

    print("=" * 60)

    print(
        f"\nFinal Score:"
        f" {score}/{len(mcqs)}"
    )

    percentage = (
        score / len(mcqs)
    ) * 100

    print(
        f"Percentage:"
        f" {percentage:.2f}%"
    )

    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    run_adaptive_quiz()