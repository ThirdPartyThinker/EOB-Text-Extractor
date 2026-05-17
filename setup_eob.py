"""Guided setup and environment check for the EOB Text Extractor.

Run this once after downloading the project:

    python setup_eob.py

It will:
  1. Check the Python version.
  2. Install the required Python packages from requirements.txt.
  3. Check that the Tesseract OCR engine and poppler are available, and
     print install instructions for this operating system if they are not.
  4. Create the eobs_in/ and eobs_out/ working folders.
  5. Run a quick offline self-test on synthetic (fake) data.
  6. Print a clear summary of what is ready and what still needs attention.

This program may use the network to install Python packages. The EOB
extraction pipeline itself never uses the network.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_PYTHON = (3, 9)

# Track problems so the final summary can report them together.
_problems: list[str] = []


def _hr() -> None:
    print("-" * 72)


def step(number: int, title: str) -> None:
    print()
    _hr()
    print(f"  STEP {number}: {title}")
    _hr()


def check_python() -> None:
    step(1, "Check Python version")
    version = sys.version_info
    print(f"  Found Python {version.major}.{version.minor}.{version.micro}")
    if (version.major, version.minor) < MIN_PYTHON:
        _problems.append(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required. "
            f"Install it from https://www.python.org/downloads/")
        print("  [X] Python is too old.")
    else:
        print("  [OK] Python version is fine.")


def install_requirements() -> None:
    step(2, "Install required Python packages")
    req = os.path.join(PROJECT_ROOT, "requirements.txt")
    if not os.path.isfile(req):
        _problems.append("requirements.txt not found next to setup_eob.py.")
        print("  [X] requirements.txt is missing.")
        return
    print("  Installing packages (this can take a minute)...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", req])
        print("  [OK] Python packages installed.")
    except subprocess.CalledProcessError:
        _problems.append(
            "pip failed to install the required packages. Check your "
            "internet connection and that Python/pip are working.")
        print("  [X] Package installation failed.")


def _system_tool_help(tool: str) -> str:
    system = platform.system()
    if tool == "tesseract":
        if system == "Windows":
            return ("Install the Tesseract OCR engine: download the 64-bit "
                    "installer from https://github.com/UB-Mannheim/tesseract/wiki "
                    "and add its folder (C:\\Program Files\\Tesseract-OCR) to PATH.")
        if system == "Darwin":
            return "Install Tesseract with: brew install tesseract"
        return "Install Tesseract with: sudo apt-get install -y tesseract-ocr"
    # poppler
    if system == "Windows":
        return ("Install poppler: download a release zip from "
                "https://github.com/oschwartz10612/poppler-windows/releases, "
                "extract it, and add its Library\\bin folder to PATH.")
    if system == "Darwin":
        return "Install poppler with: brew install poppler"
    return "Install poppler with: sudo apt-get install -y poppler-utils"


def check_system_tools() -> None:
    step(3, "Check OCR tools (Tesseract and poppler)")
    # Tesseract provides the `tesseract` command; poppler provides `pdftoppm`.
    for label, command in (("Tesseract OCR engine", "tesseract"),
                            ("poppler", "pdftoppm")):
        if shutil.which(command):
            print(f"  [OK] {label} found.")
        else:
            tool = "tesseract" if command == "tesseract" else "poppler"
            msg = _system_tool_help(tool)
            _problems.append(f"{label} not found. {msg}")
            print(f"  [!] {label} NOT found.")
            print(f"      {msg}")
    print()
    print("  Note: Tesseract and poppler are only needed for SCANNED/image")
    print("  EOBs. Normal digital PDFs work without them.")


def make_folders() -> None:
    step(4, "Create working folders")
    for name in ("eobs_in", "eobs_out"):
        path = os.path.join(PROJECT_ROOT, name)
        os.makedirs(path, exist_ok=True)
        print(f"  [OK] {name}/ ready")
    print()
    print("  Put EOB PDFs into eobs_in/ ; results appear in eobs_out/")


def self_test() -> None:
    step(5, "Run a quick self-test on synthetic (fake) data")
    try:
        # Imported here so step 2 has already installed dependencies.
        sys.path.insert(0, PROJECT_ROOT)
        from eob_extract import extract_text
        from generate_synthetic_eobs import SYNTHETIC_EOBS, make_text_pdf

        with tempfile.TemporaryDirectory() as tmp:
            pdf = os.path.join(tmp, "selftest.pdf")
            make_text_pdf(SYNTHETIC_EOBS[0], pdf)
            text, metadata = extract_text(pdf)
        if "TEST PATIENT 001" in text and metadata["char_count"] > 50:
            print("  [OK] Self-test passed: synthetic EOB extracted correctly.")
        else:
            _problems.append("Self-test ran but produced unexpected output.")
            print("  [X] Self-test produced unexpected output.")
    except Exception as exc:  # dependency or runtime failure
        _problems.append(f"Self-test failed to run: {type(exc).__name__}: {exc}")
        print(f"  [X] Self-test could not run ({type(exc).__name__}).")


def summary() -> int:
    print()
    print("=" * 72)
    if not _problems:
        print("  SETUP COMPLETE - everything is ready.")
        print()
        print("  To convert EOBs:")
        print("    1. Put EOB PDF files into the eobs_in/ folder.")
        print("    2. Run:  python run_batch.py --input eobs_in --output eobs_out")
        print("       (on Windows you can double-click run_extractor.bat)")
        print("    3. Collect the .txt files from the eobs_out/ folder.")
        print("=" * 72)
        return 0
    print(f"  SETUP FINISHED WITH {len(_problems)} ITEM(S) NEEDING ATTENTION:")
    print("=" * 72)
    for i, problem in enumerate(_problems, 1):
        print(f"  {i}. {problem}")
    print("=" * 72)
    print("  Fix the items above, then run  python setup_eob.py  again.")
    return 1


def main() -> int:
    print()
    print("=" * 72)
    print("  EOB TEXT EXTRACTOR - SETUP")
    print("=" * 72)
    print("  HIPAA: install and use this tool only on a HIPAA-compliant")
    print("  computer. Never process real EOBs on Google Colab or other")
    print("  consumer cloud notebooks. Setup uses synthetic (fake) data only.")

    check_python()
    install_requirements()
    check_system_tools()
    make_folders()
    self_test()
    return summary()


if __name__ == "__main__":
    raise SystemExit(main())
