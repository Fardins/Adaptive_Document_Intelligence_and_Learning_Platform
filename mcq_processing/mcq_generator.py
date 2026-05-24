"""
mcq_generator.py
================
Generate high-quality exam-style MCQs using the Groq LLM.

Features:
  - Creates reasoning-focused multiple choice questions.
  - Generates realistic distractors.
  - Randomizes option positions automatically.
  - Prevents repetitive answer patterns.
  - Produces concise educational explanations.
  - Strict JSON parsing for reliable output.

Workflow:
  Text Chunk
      ↓
  Groq LLM Generation
      ↓
  JSON Validation
      ↓
  Option Shuffling
      ↓
  Final MCQ Set

Public API:
  generate_mcqs(chunk_text, n_questions)
      → generate MCQs from text content

Internal Utilities:
  shuffle_options(mcq)
      → randomize answer positions safely
"""

import json
import os
import random

from groq import Groq
from dotenv import load_dotenv
from config import GROQ_MODEL

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
# OPTION SHUFFLER
# ══════════════════════════════════════════════════════════════════════════════

def shuffle_options(mcq):
    """
    Randomize option positions while preserving correct answer.
    """

    options = mcq["options"]

    items = list(options.items())

    random.shuffle(items)

    labels = ["A", "B", "C", "D"]

    new_options = {}

    correct_text = options[mcq["correct_answer"]]

    new_correct = None

    for idx, (_, value) in enumerate(items):

        label = labels[idx]

        new_options[label] = value

        if value == correct_text:
            new_correct = label

    mcq["options"] = new_options
    mcq["correct_answer"] = new_correct

    return mcq


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_mcqs(chunk_text, n_questions=5):

    prompt = f"""
You are an expert university exam question setter.

Generate EXACTLY {n_questions} high-quality MCQs from the text.

IMPORTANT RULES:

1. Questions must test understanding, reasoning, and comprehension.
2. Avoid trivial wording.
3. Create realistic distractors.
4. Correct answers MUST NOT follow repetitive patterns.
5. Distribute correct answers naturally across A/B/C/D.
6. Keep explanations concise and educational.
7. Output ONLY valid JSON.
8. No markdown.
9. No extra text.

OUTPUT FORMAT:

[
  {{
    "question": "...",
    "options": {{
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    }},
    "correct_answer": "A",
    "explanation": "..."
  }}
]

TEXT:
\"\"\"
{chunk_text}
\"\"\"
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8,
    )

    content = response.choices[0].message.content.strip()

    # ──────────────────────────────────────────────────────────────────────
    # CLEAN JSON
    # ──────────────────────────────────────────────────────────────────────

    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:

        mcqs = json.loads(content)

    except Exception:

        print("\n❌ Failed to parse JSON response\n")
        print(content)

        raise

    # ──────────────────────────────────────────────────────────────────────
    # SHUFFLE OPTIONS
    # ──────────────────────────────────────────────────────────────────────

    shuffled_mcqs = []

    for mcq in mcqs:

        shuffled_mcq = shuffle_options(mcq)

        shuffled_mcqs.append(shuffled_mcq)

    return shuffled_mcqs