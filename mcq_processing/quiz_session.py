"""
quiz_session.py
===============
Interactive terminal-based MCQ quiz system.

Features:
  - Generates quizzes dynamically from stored content.
  - Supports section-level and chunk-level quizzes.
  - Interactive answer input validation.
  - Real-time scoring system.
  - Displays explanations for incorrect answers.
  - Calculates final percentage score.

Quiz Flow:
  Retrieve Content
        ↓
  Generate MCQs
        ↓
  Interactive Quiz Session
        ↓
  Score Evaluation
        ↓
  Final Result Summary

Supported Inputs:
  4.7
      → full section quiz

  4.7::0
      → single chunk quiz

Public API:
  run_quiz(content_id, n_questions)
      → start an interactive quiz session
"""

# When running this file directly (e.g. `python mcq_processing/quiz_session.py`),
# ensure the project root is on sys.path so sibling packages (like
# `input_processing`) can be imported.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcq_processing.quiz_engine import get_content
from mcq_processing.mcq_generator import generate_mcqs


def run_quiz(content_id, n_questions=5):

    # ──────────────────────────────────────────────────────────────────────
    # GET CONTENT
    # ──────────────────────────────────────────────────────────────────────

    content = get_content(content_id)

    if not content:

        print(f"\n❌ No content found: {content_id}")
        return

    text = content["text"]

    print("\n══════════════════════════════════════════════")
    print(f" QUIZ SESSION → {content_id}")
    print("══════════════════════════════════════════════")

    print("\nGenerating MCQs using Groq LLM...\n")

    mcqs = generate_mcqs(
        chunk_text=text,
        n_questions=n_questions
    )

    # ──────────────────────────────────────────────────────────────────────
    # QUIZ LOOP
    # ──────────────────────────────────────────────────────────────────────

    score = 0

    for idx, mcq in enumerate(mcqs, start=1):

        print("\n" + "─" * 60)

        print(f"\nQ{idx}. {mcq['question']}\n")

        for key, value in mcq["options"].items():

            print(f"  {key}. {value}")

        while True:

            answer = input("\nYour Answer (A/B/C/D): ").strip().upper()

            if answer in ["A", "B", "C", "D"]:
                break

            print("Invalid input.")

        correct = mcq["correct_answer"].upper()

        # ──────────────────────────────────────────────────────────────
        # CORRECT
        # ──────────────────────────────────────────────────────────────

        if answer == correct:

            print("\n✅ Correct!")

            score += 1

        # ──────────────────────────────────────────────────────────────
        # WRONG
        # ──────────────────────────────────────────────────────────────

        else:

            print("\n❌ Wrong!")

            print(f"\nCorrect Answer: {correct}")

            print(f"\nExplanation:")
            print(mcq["explanation"])

    # ──────────────────────────────────────────────────────────────────────
    # FINAL SCORE
    # ──────────────────────────────────────────────────────────────────────

    print("\n")
    print("══════════════════════════════════════════════")
    print(" QUIZ COMPLETE")
    print("══════════════════════════════════════════════")

    print(f"\nFinal Score: {score}/{len(mcqs)}")

    percentage = (score / len(mcqs)) * 100

    print(f"Percentage : {percentage:.2f}%\n")


if __name__ == "__main__":

    print()

    content_id = input(
        "Enter section_id or chunk_id\n"
        "(examples: 4.7 or 4.7::0): "
    ).strip()

    n = input("Number of MCQs: ").strip()

    n_questions = int(n) if n.isdigit() else 5

    run_quiz(
        content_id=content_id,
        n_questions=n_questions
    )