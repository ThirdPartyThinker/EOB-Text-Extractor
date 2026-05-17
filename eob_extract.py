"""EOB PDF-to-text extraction core module.

Converts dental Explanation of Benefits (EOB) PDFs to plain text fully
offline using only free, open-source libraries. No network calls are made
during PDF processing.

Public API:
    print_hipaa_warning()        -- print the startup HIPAA notice
    extract_text(pdf_path, ...)  -- extract text + metadata from one PDF
    extract_eob_fields(text)     -- best-effort regex field extraction
"""

from __future__ import annotations

import logging
import os
import re
import time
from datetime import datetime, timezone

import pdfplumber
from pypdf import PdfReader

# OCR dependencies are imported lazily inside _extract_with_ocr() so that
# text-only workflows do not require Tesseract/poppler to be installed.

logger = logging.getLogger("eob_extract")

# Default: if pdfplumber yields fewer than this many characters per page on
# average, the PDF is treated as scanned/image-based and OCR is used instead.
DEFAULT_OCR_THRESHOLD = 50

HIPAA_WARNING = """
================================================================================
  HIPAA NOTICE
  Real Protected Health Information (PHI) may ONLY be processed on a
  HIPAA-compliant environment with appropriate safeguards.

  DO NOT process real EOBs on free Google Colab or consumer cloud notebooks.
  Those environments are NOT HIPAA-compliant. Use SYNTHETIC data only there.
================================================================================
"""

_hipaa_warning_shown = False


def print_hipaa_warning(force: bool = False) -> None:
    """Print the HIPAA warning to stdout (once per process unless forced)."""
    global _hipaa_warning_shown
    if _hipaa_warning_shown and not force:
        return
    print(HIPAA_WARNING)
    _hipaa_warning_shown = True


def _page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF."""
    reader = PdfReader(pdf_path)
    return len(reader.pages)


def _extract_with_pdfplumber(pdf_path: str) -> tuple[str, int]:
    """Extract embedded text with pdfplumber. Returns (text, page_count)."""
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages), len(pages)


def _extract_with_ocr(pdf_path: str) -> tuple[str, int]:
    """Extract text via OCR (pdf2image + pytesseract). Returns (text, pages)."""
    # Lazy import: only needed when the OCR fallback path runs.
    import pytesseract
    from pdf2image import convert_from_path

    images = convert_from_path(pdf_path)
    pages = [pytesseract.image_to_string(img) for img in images]
    return "\n".join(pages), len(pages)


def extract_text(
    pdf_path: str,
    ocr_threshold: int = DEFAULT_OCR_THRESHOLD,
) -> tuple[str, dict]:
    """Extract plain text from a single PDF.

    Tries pdfplumber text extraction first. If the average extracted
    characters per page falls below ``ocr_threshold``, falls back to OCR.

    Returns:
        (text, metadata) where metadata contains only non-PHI fields:
        filename, page_count, extraction_method, char_count,
        processing_seconds, timestamp_iso.
    """
    filename = os.path.basename(pdf_path)
    start = time.monotonic()

    text, page_count = _extract_with_pdfplumber(pdf_path)
    method = "pdfplumber"

    avg_chars = (len(text) / page_count) if page_count else 0
    if avg_chars < ocr_threshold:
        logger.info("%s: low text yield (%.1f chars/page), using OCR", filename, avg_chars)
        try:
            ocr_text, ocr_pages = _extract_with_ocr(pdf_path)
            text, page_count = ocr_text, ocr_pages
            method = "ocr"
        except Exception as exc:  # OCR deps missing or render failure
            logger.warning("%s: OCR fallback unavailable (%s); keeping pdfplumber output",
                            filename, type(exc).__name__)

    elapsed = round(time.monotonic() - start, 3)
    metadata = {
        "filename": filename,
        "page_count": page_count,
        "extraction_method": method,
        "char_count": len(text),
        "processing_seconds": elapsed,
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
    }
    # Log filename + method only. Never log file contents or text snippets.
    logger.info("Extracted %s via %s (%d pages, %d chars, %.3fs)",
                filename, method, page_count, len(text), elapsed)
    return text, metadata


# --- Best-effort structured field extraction ---------------------------------
#
# NOTE: regex extraction is BEST-EFFORT only. EOB layouts vary widely between
# payers, so these patterns will not match every template. Treat the results
# as a convenience, not a source of truth, and verify against the raw text.

_FIELD_PATTERNS = {
    "claim_number": re.compile(
        r"claim\s*(?:number|no\.?|#)?\s*[:#]?\s*([A-Z0-9][A-Z0-9\-]{4,})", re.I),
    "date_of_service": re.compile(
        r"date\s*of\s*service\s*[:#]?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", re.I),
    "billed_amount": re.compile(
        r"(?:billed|charged?|total\s*charge)\s*(?:amount)?\s*[:#]?\s*"
        r"\$?\s*([\d,]+\.\d{2})", re.I),
    "paid_amount": re.compile(
        r"(?:paid|payment|plan\s*paid|amount\s*paid)\s*(?:amount)?\s*[:#]?\s*"
        r"\$?\s*([\d,]+\.\d{2})", re.I),
    "patient_responsibility": re.compile(
        r"patient\s*(?:responsibility|resp\.?|portion|owes?)\s*[:#]?\s*"
        r"\$?\s*([\d,]+\.\d{2})", re.I),
}

# CDT codes: 'D' followed by 4 digits. CPT codes: standalone 5-digit numbers.
_CDT_PATTERN = re.compile(r"\bD\d{4}\b")
_CPT_PATTERN = re.compile(r"\b\d{5}\b")


def extract_eob_fields(text: str) -> dict:
    """Best-effort regex extraction of common EOB fields.

    Returns a dict with a stable shape (keys always present):
        claim_number, date_of_service, billed_amount, paid_amount,
        patient_responsibility -> str or None
        procedure_codes -> sorted list of unique CDT/CPT codes found

    Regex extraction is best-effort and varies by payer template; missing
    fields are returned as None rather than raising.
    """
    result: dict = {
        "claim_number": None,
        "date_of_service": None,
        "billed_amount": None,
        "paid_amount": None,
        "patient_responsibility": None,
        "procedure_codes": [],
    }
    if not text:
        return result

    for field, pattern in _FIELD_PATTERNS.items():
        match = pattern.search(text)
        if match:
            result[field] = match.group(1).strip()

    codes = set(_CDT_PATTERN.findall(text))
    # CPT codes only if they are not already counted as a CDT code's digits.
    codes.update(_CPT_PATTERN.findall(text))
    result["procedure_codes"] = sorted(codes)
    return result


# Print the HIPAA warning when this module is imported for interactive use.
print_hipaa_warning()
