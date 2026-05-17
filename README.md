# EOB Text Extractor

**⚠️ HIPAA NOTICE — READ FIRST**

**Real Explanation of Benefits (EOB) documents contain Protected Health
Information (PHI). Process real EOBs ONLY on a HIPAA-compliant local
environment with appropriate safeguards (encryption at rest, access
controls, audit logging). Google Colab is NOT HIPAA-compliant. Use
synthetic data only in Colab. For real EOBs, run this tool on a
HIPAA-compliant local environment with appropriate safeguards (encryption,
access controls, audit logging).**

---

A Python tool that converts dental EOB PDFs into plain text files. It runs
**fully offline** using only free, open-source libraries — no calls to
OpenAI, Anthropic, AWS, Google Cloud, Azure, or any external API at any
point in the pipeline. It works with networking disabled.

## How it works

1. **Auto-detect PDF type.** Text extraction is attempted first with
   `pdfplumber`. If the average extracted characters per page falls below a
   configurable threshold (default `50`), the tool falls back to OCR using
   `pytesseract` + `pdf2image`.
2. **Batch mode.** Point it at an input directory of PDFs; it writes one
   `.txt` per PDF to an output directory, preserving filenames.
3. **Sidecar metadata.** A `.json` is written next to each `.txt` containing
   metadata only — `filename`, `page_count`, `extraction_method`,
   `char_count`, `processing_seconds`, `timestamp_iso`. **The sidecar never
   contains extracted PHI.**
4. **Optional structured extraction.** `extract_eob_fields(text)` uses regex
   to pull common EOB fields. This is **best-effort** and varies by payer
   template (see below).
5. **Logging.** Filenames and extraction methods are logged to stdout. File
   contents and extracted text are **never** logged.

## Files

| File | Purpose |
|------|---------|
| `eob_extract.py` | Core module: `extract_text()`, `extract_eob_fields()` |
| `run_batch.py` | CLI batch processor |
| `generate_synthetic_eobs.py` | Creates fake EOB PDFs for testing |
| `eob_extract_colab.ipynb` | Google Colab demo notebook (synthetic data only) |
| `tests/test_extract.py` | Pytest suite |
| `requirements.txt` | Pinned dependency versions |

## Installation

### Google Colab (synthetic data only)

```python
# Cell — system dependencies
!apt-get update && apt-get install -y tesseract-ocr poppler-utils

# Cell — Python dependencies
!pip install -r requirements.txt
```

Then run the notebook `eob_extract_colab.ipynb`. **Do not upload real EOBs
to Colab.**

### Local install

The Python packages install the same way everywhere:

```bash
pip install -r requirements.txt
```

You also need two system tools — the **Tesseract** OCR engine and
**poppler** (used by `pdf2image` to render PDF pages):

**Windows**
- Tesseract: install the UB Mannheim build from
  <https://github.com/UB-Mannheim/tesseract/wiki>. Add its install folder to
  your `PATH` (or set `pytesseract.pytesseract.tesseract_cmd`).
- poppler: install via `conda install -c conda-forge poppler`, or download a
  poppler release zip (e.g. from the `oschwartz10612/poppler-windows`
  releases) and add its `bin/` folder to `PATH`.

**macOS**
```bash
brew install tesseract poppler
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt-get install -y tesseract-ocr poppler-utils
```

## Usage

### Generate synthetic test PDFs

```bash
python generate_synthetic_eobs.py --output ./synthetic_in
```

### Batch processing

```bash
python run_batch.py --input ./synthetic_in --output ./synthetic_out
```

Optionally tune the OCR threshold (average chars/page below which OCR runs):

```bash
python run_batch.py --input ./in --output ./out --ocr-threshold 80
```

### Single file (from Python)

```python
from eob_extract import extract_text, extract_eob_fields

text, metadata = extract_text("path/to/eob.pdf")
print(metadata)            # non-PHI metadata only
fields = extract_eob_fields(text)
print(fields)              # best-effort structured fields
```

### Run the tests

```bash
pip install -r requirements.txt
pytest
```

(The OCR fallback test is skipped automatically if Tesseract is not installed.)

## Best-effort field extraction

`extract_eob_fields(text)` returns a dict with a stable shape:

```python
{
  "claim_number": str | None,
  "date_of_service": str | None,
  "billed_amount": str | None,
  "paid_amount": str | None,
  "patient_responsibility": str | None,
  "procedure_codes": [str, ...],   # CDT (Dxxxx) / CPT (5-digit) codes
}
```

**Regex extraction is best-effort and varies by payer template.** EOB
layouts differ widely between insurers; fields that do not match a pattern
are returned as `None`. Always verify against the raw extracted text.

## Dependency licenses

All dependencies are free and open-source:

| Package | License |
|---------|---------|
| pdfplumber | MIT |
| pypdf | BSD |
| pytesseract | Apache 2.0 |
| pdf2image | MIT |
| Pillow | HPND (PIL/open-source) |
| reportlab | BSD (used only to generate synthetic test PDFs) |
| pytest | MIT |

System tools: **Tesseract OCR** (Apache 2.0) and **poppler** (GPL-2.0).

## HIPAA compliance reminder

**Google Colab is not HIPAA-compliant. Use synthetic data only in Colab.
For real EOBs, run this tool on a HIPAA-compliant local environment with
appropriate safeguards (encryption, access controls, audit logging).**
