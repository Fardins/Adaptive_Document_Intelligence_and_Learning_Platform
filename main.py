"""
main.py
========
Main pipeline controller for the Adaptive Document Preparation System.

Workflow:
1. Check whether ChromaDB already contains processed document data
2. If storage is empty:
      → Run document parsing + chunking + embedding pipeline
3. Launch adaptive quiz engine
4. Allow repeated quiz sessions without reprocessing documents

Features:
- Automatic pipeline orchestration
- Smart ChromaDB existence detection
- Separate process execution for module isolation
- Crash handling with debugging guidance
- Continuous adaptive quiz loop support
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
from config import CHROMA_PATH


def chroma_store_exists() -> bool:
    """
    Check whether ChromaDB already contains processed data.
    """

    if not CHROMA_PATH.exists():
        return False

    # folder exists but empty
    if not any(CHROMA_PATH.iterdir()):
        return False

    return True


def run_module(module: str, args: List[str] = None) -> None:
    """
    Run a module as a separate Python process.
    """

    cmd = [sys.executable, "-m", module]

    if args:
        cmd.extend(args)

    print("\n" + "=" * 72)
    print(f"Running: {module}")
    print("Command:", " ".join(cmd))
    print("=" * 72 + "\n")

    rc = subprocess.call(cmd)

    if rc != 0:
        # On Windows an access violation in a native extension shows
        # up as exit code 3221225477 (0xC0000005). That usually means
        # a native library (chromadb Rust binding, onnxruntime, torch,
        # etc.) crashed. Provide a helpful hint to the user.
        print(f"\n❌ Module {module} exited with code {rc}")

        if rc == 3221225477:
            print("\nPossible cause: native extension crash (access violation).")
            print("Try: delete ./chroma_store and section_map.json, then run the module directly:")
            print("  python -X faulthandler -m input_processing.main <pdf-path>")
            print("Also ensure you use the same Python interpreter where packages are installed.")

        sys.exit(rc)


def main():

    # ==========================================================
    # STEP 1 → Run input processing ONLY if ChromaDB is empty
    # ==========================================================

    if not chroma_store_exists():

        print("\n📦 Chroma store is empty.")
        print("➡ Running input processing pipeline...\n")

        run_module("input_processing.main")

    else:
        print("\n✅ Existing Chroma store detected.")
        print("⏩ Skipping input processing.\n")

    # ==========================================================
    # STEP 2 → Run adaptive quiz repeatedly
    # ==========================================================

    while True:

        run_module("adaptivity_processing.adaptive_quiz")

        again = input(
            "\nDo you want to run another adaptive quiz? (y/n): "
        ).strip().lower()

        if again != "y":
            print("\n👋 Exiting pipeline.")
            break


if __name__ == "__main__":
    main()