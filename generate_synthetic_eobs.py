"""Generate synthetic (fake) dental EOB PDFs for testing.

Produces a mix of:
  * text-based PDFs  -- exercise the pdfplumber extraction path
  * image-rendered PDFs -- exercise the OCR fallback path

ALL DATA IS OBVIOUSLY FAKE. Patient names are "TEST PATIENT NNN", the SSN is
always "000-00-0000", the payer is "FAKE INSURANCE CO", and claim numbers are
clearly invented. This script never produces or touches real PHI.

Usage:
    python generate_synthetic_eobs.py --output ./synthetic_in
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Synthetic EOB records. Everything here is invented test data. -----------
SYNTHETIC_EOBS = [
    {
        "patient": "TEST PATIENT 001",
        "ssn": "000-00-0000",
        "payer": "FAKE INSURANCE CO",
        "claim_number": "FAKE-CLAIM-1001",
        "date_of_service": "01/15/2026",
        "procedure": "D1110",
        "procedure_desc": "Prophylaxis - adult",
        "billed": "150.00",
        "paid": "120.00",
        "patient_resp": "30.00",
    },
    {
        "patient": "TEST PATIENT 002",
        "ssn": "000-00-0000",
        "payer": "FAKE INSURANCE CO",
        "claim_number": "FAKE-CLAIM-1002",
        "date_of_service": "02/03/2026",
        "procedure": "D2740",
        "procedure_desc": "Crown - porcelain/ceramic",
        "billed": "1200.00",
        "paid": "780.00",
        "patient_resp": "420.00",
    },
    {
        "patient": "TEST PATIENT 003",
        "ssn": "000-00-0000",
        "payer": "FAKE INSURANCE CO",
        "claim_number": "FAKE-CLAIM-1003",
        "date_of_service": "03/22/2026",
        "procedure": "D0274",
        "procedure_desc": "Bitewings - four radiographic images",
        "billed": "85.00",
        "paid": "85.00",
        "patient_resp": "0.00",
    },
    {
        "patient": "TEST PATIENT 004",
        "ssn": "000-00-0000",
        "payer": "FAKE INSURANCE CO",
        "claim_number": "FAKE-CLAIM-1004",
        "date_of_service": "04/09/2026",
        "procedure": "D7140",
        "procedure_desc": "Extraction - erupted tooth",
        "billed": "295.00",
        "paid": "206.50",
        "patient_resp": "88.50",
    },
]


def _eob_lines(eob: dict) -> list[str]:
    """Render one synthetic EOB record as a list of text lines."""
    return [
        "EXPLANATION OF BENEFITS (SYNTHETIC TEST DOCUMENT)",
        "",
        f"Payer: {eob['payer']}",
        f"Patient Name: {eob['patient']}",
        f"Patient SSN: {eob['ssn']}",
        "",
        f"Claim Number: {eob['claim_number']}",
        f"Date of Service: {eob['date_of_service']}",
        "",
        "Procedure Detail:",
        f"  Procedure Code: {eob['procedure']}",
        f"  Description: {eob['procedure_desc']}",
        "",
        f"Billed Amount: ${eob['billed']}",
        f"Paid Amount: ${eob['paid']}",
        f"Patient Responsibility: ${eob['patient_resp']}",
        "",
        "This is fake data generated for software testing only.",
    ]


def make_text_pdf(eob: dict, path: Path) -> None:
    """Create a text-based PDF (selectable text -> pdfplumber path)."""
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 72
    c.setFont("Helvetica", 12)
    for line in _eob_lines(eob):
        c.drawString(72, y, line)
        y -= 20
    c.showPage()
    c.save()


def make_image_pdf(eob: dict, path: Path) -> None:
    """Create an image-only PDF (no selectable text -> OCR fallback path)."""
    width, height = 1275, 1650  # ~letter at 150 DPI
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    y = 80
    for line in _eob_lines(eob):
        draw.text((80, y), line, fill="black", font=font)
        y += 48
    # Saving an RGB image as PDF yields an image-only (scanned-style) PDF.
    img.save(str(path), "PDF", resolution=150.0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic EOB PDFs.")
    parser.add_argument("--output", default="./synthetic_in",
                        help="Directory to write synthetic PDFs into")
    args = parser.parse_args(argv)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # First three records -> text-based PDFs; remainder -> image-rendered PDFs.
    for i, eob in enumerate(SYNTHETIC_EOBS):
        if i < 3:
            target = out_dir / f"synthetic_text_{i + 1:03d}.pdf"
            make_text_pdf(eob, target)
            kind = "text-based"
        else:
            target = out_dir / f"synthetic_image_{i + 1:03d}.pdf"
            make_image_pdf(eob, target)
            kind = "image-rendered"
        print(f"  created {target.name}  ({kind})")

    print(f"Generated {len(SYNTHETIC_EOBS)} synthetic EOB PDFs in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
