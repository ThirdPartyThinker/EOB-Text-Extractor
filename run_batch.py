"""Batch CLI: convert every PDF in an input directory to a .txt file.

Usage:
    python run_batch.py --input ./in --output ./out
    python run_batch.py --input ./in --output ./out --ocr-threshold 80

For each ``<name>.pdf`` in the input directory this writes:
    <output>/<name>.txt   -- extracted plain text
    <output>/<name>.json  -- non-PHI metadata sidecar

It also writes one combined worksheet for the whole batch:
    <output>/eob_fields.csv  -- one row per EOB, best-effort structured
                                fields for review and manual entry

The ``.json`` sidecar contains METADATA ONLY and never any extracted
PHI/text. The ``eob_fields.csv`` worksheet DOES contain extracted EOB
field values (claim numbers, amounts, dates, codes) and must be handled
as PHI: keep it inside your secured, HIPAA-compliant storage.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

from eob_extract import (
    DEFAULT_OCR_THRESHOLD,
    extract_eob_fields,
    extract_text,
    print_hipaa_warning,
)

logger = logging.getLogger("eob_extract")

# Column order for the combined eob_fields.csv worksheet.
CSV_COLUMNS = [
    "filename",
    "claim_number",
    "date_of_service",
    "billed_amount",
    "paid_amount",
    "patient_responsibility",
    "procedure_codes",
]

FIELDS_CSV_NAME = "eob_fields.csv"


def _fields_to_row(filename: str, fields: dict) -> dict:
    """Flatten an extract_eob_fields() dict into one CSV row."""
    row = {"filename": filename}
    for key in CSV_COLUMNS[1:]:
        value = fields.get(key)
        if isinstance(value, list):
            value = "; ".join(value)
        row[key] = "" if value is None else value
    return row


def process_directory(input_dir: Path, output_dir: Path, ocr_threshold: int) -> int:
    """Process every PDF in ``input_dir``. Returns the number of files done."""
    pdfs = sorted(p for p in input_dir.iterdir()
                  if p.is_file() and p.suffix.lower() == ".pdf")

    if not pdfs:
        logger.info("No PDF files found in %s; nothing to do.", input_dir)
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    processed = 0
    field_rows: list[dict] = []

    for pdf_path in pdfs:
        try:
            text, metadata = extract_text(str(pdf_path), ocr_threshold=ocr_threshold)
        except Exception as exc:
            logger.error("Failed to process %s: %s", pdf_path.name, type(exc).__name__)
            continue

        txt_path = output_dir / (pdf_path.stem + ".txt")
        json_path = output_dir / (pdf_path.stem + ".json")

        txt_path.write_text(text, encoding="utf-8")
        # Sidecar = metadata only. extract_text() guarantees no PHI here.
        json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        # Best-effort structured fields for the combined worksheet.
        fields = extract_eob_fields(text)
        field_rows.append(_fields_to_row(pdf_path.name, fields))

        logger.info("Wrote %s and %s", txt_path.name, json_path.name)
        processed += 1

    if field_rows:
        csv_path = output_dir / FIELDS_CSV_NAME
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(field_rows)
        logger.info("Wrote %s (%d row(s))", FIELDS_CSV_NAME, len(field_rows))

    return processed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Batch-convert EOB PDFs to plain text (offline, HIPAA-aware).")
    parser.add_argument("--input", required=True, help="Input directory of PDFs")
    parser.add_argument("--output", required=True, help="Output directory for results")
    parser.add_argument("--ocr-threshold", type=int, default=DEFAULT_OCR_THRESHOLD,
                        help=f"Avg chars/page below which OCR is used "
                             f"(default {DEFAULT_OCR_THRESHOLD})")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print_hipaa_warning()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.is_dir():
        logger.error("Input directory does not exist: %s", input_dir)
        return 1

    count = process_directory(input_dir, output_dir, args.ocr_threshold)
    logger.info("Done. Processed %d PDF file(s).", count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
