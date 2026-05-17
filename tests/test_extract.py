"""Pytest suite for the EOB text extractor.

Tests run fully offline. They generate their own synthetic PDFs in a temp
directory, so no fixtures or real data are required.
"""

from __future__ import annotations

import json
import shutil

import pytest

import eob_extract
from eob_extract import extract_eob_fields, extract_text
from generate_synthetic_eobs import SYNTHETIC_EOBS, make_image_pdf, make_text_pdf
from run_batch import process_directory

_OCR_AVAILABLE = shutil.which("tesseract") is not None


@pytest.fixture
def text_pdf(tmp_path):
    path = tmp_path / "synthetic_text.pdf"
    make_text_pdf(SYNTHETIC_EOBS[0], path)
    return path


@pytest.fixture
def image_pdf(tmp_path):
    path = tmp_path / "synthetic_image.pdf"
    make_image_pdf(SYNTHETIC_EOBS[1], path)
    return path


def test_text_extraction_on_text_pdf(text_pdf):
    """pdfplumber path extracts selectable text from a text-based PDF."""
    text, metadata = extract_text(str(text_pdf))
    assert metadata["extraction_method"] == "pdfplumber"
    assert "TEST PATIENT 001" in text
    assert "FAKE-CLAIM-1001" in text
    assert metadata["char_count"] > 50


@pytest.mark.skipif(not _OCR_AVAILABLE, reason="Tesseract not installed")
def test_ocr_fallback_on_image_pdf(image_pdf):
    """OCR fallback triggers for an image-rendered PDF with no embedded text."""
    text, metadata = extract_text(str(image_pdf))
    assert metadata["extraction_method"] == "ocr"
    # OCR is fuzzy; check a distinctive token survives recognition.
    assert "FAKE" in text.upper()


def test_image_pdf_has_low_text_yield(image_pdf):
    """An image-only PDF must yield near-zero text via pdfplumber."""
    raw_text, page_count = eob_extract._extract_with_pdfplumber(str(image_pdf))
    avg = len(raw_text) / page_count if page_count else 0
    assert avg < eob_extract.DEFAULT_OCR_THRESHOLD


def test_sidecar_keys_and_no_phi(tmp_path, text_pdf):
    """Sidecar JSON has the expected metadata keys and contains no PHI/text."""
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    shutil.copy(text_pdf, in_dir / "synthetic_text.pdf")

    process_directory(in_dir, out_dir, eob_extract.DEFAULT_OCR_THRESHOLD)

    sidecar = json.loads((out_dir / "synthetic_text.json").read_text())
    expected = {"filename", "page_count", "extraction_method", "char_count",
                "processing_seconds", "timestamp_iso"}
    assert set(sidecar.keys()) == expected

    # Sidecar must NOT carry an extracted-text/content field...
    assert "text" not in sidecar
    assert "content" not in sidecar
    # ...nor any extracted PHI values.
    blob = json.dumps(sidecar)
    for phi in ("TEST PATIENT", "000-00-0000", "FAKE-CLAIM"):
        assert phi not in blob


def test_batch_empty_input_directory(tmp_path):
    """Batch processor handles an empty input directory gracefully."""
    in_dir = tmp_path / "empty_in"
    out_dir = tmp_path / "empty_out"
    in_dir.mkdir()
    count = process_directory(in_dir, out_dir, eob_extract.DEFAULT_OCR_THRESHOLD)
    assert count == 0


def test_extract_eob_fields_shape(text_pdf):
    """extract_eob_fields returns a stable dict shape on a synthetic EOB."""
    text, _ = extract_text(str(text_pdf))
    fields = extract_eob_fields(text)

    expected_keys = {"claim_number", "date_of_service", "billed_amount",
                     "paid_amount", "patient_responsibility", "procedure_codes"}
    assert set(fields.keys()) == expected_keys
    assert isinstance(fields["procedure_codes"], list)

    assert fields["claim_number"] == "FAKE-CLAIM-1001"
    assert fields["date_of_service"] == "01/15/2026"
    assert fields["billed_amount"] == "150.00"
    assert "D1110" in fields["procedure_codes"]


def test_extract_eob_fields_empty_text():
    """Empty input still yields the stable shape with None values."""
    fields = extract_eob_fields("")
    assert fields["claim_number"] is None
    assert fields["procedure_codes"] == []
