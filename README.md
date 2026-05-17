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

> ### 🦷 Dental clinic staff: start here
>
> If you work at a clinic and just want to convert real EOB PDFs to text,
> **follow [`CLINIC_GUIDE.md`](CLINIC_GUIDE.md)** — a plain-language,
> step-by-step Windows guide with no programming required. You can ignore
> the rest of this README, which is written for software developers and
> covers testing with synthetic data.

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

Open `eob_extract_colab.ipynb` in Colab and run the cells top to bottom.
Colab starts with an empty working directory, so the notebook's **first
cell clones this repository** before anything else — otherwise commands
like `pip install -r requirements.txt` fail with
`Could not open requirements file`. The remaining cells install the
system and Python dependencies:

```python
# Cell 1 — clone the repo (required: Colab has no project files yet)
!git clone https://github.com/ThirdPartyThinker/EOB-Text-Extractor.git
%cd EOB-Text-Extractor

# Cell 2 — system dependencies
!apt-get update && apt-get install -y tesseract-ocr poppler-utils

# Cell 3 — Python dependencies
!pip install -r requirements.txt
```

**Do not upload real EOBs to Colab.**

### Local install

The Python packages install the same way everywhere:

```bash
pip install -r requirements.txt
```

You also need two system tools — the **Tesseract** OCR engine and
**poppler** (used by `pdf2image` to render PDF pages):

**Windows** — see the [full Windows step-by-step guide](#windows-step-by-step-guide)
below. In brief:
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

## Windows step-by-step guide

This section walks through a complete Windows setup and day-to-day use,
assuming no prior Python experience. Run it on a **HIPAA-compliant
machine** if you will process real EOBs.

### Part A — One-time installation

**Step 1 — Install Python**

1. Go to <https://www.python.org/downloads/windows/> and download the
   latest Python 3 (64-bit) installer.
2. Run the installer. On the first screen, **check the box
   "Add python.exe to PATH"**, then click "Install Now".
3. Verify it worked: open the Start menu, type `cmd`, open
   **Command Prompt**, and run:
   ```bat
   python --version
   ```
   You should see something like `Python 3.12.x`.

**Step 2 — Install Tesseract (the OCR engine)**

1. Download the Windows installer from the UB Mannheim build page:
   <https://github.com/UB-Mannheim/tesseract/wiki>
2. Run it. Note the install folder — by default
   `C:\Program Files\Tesseract-OCR`.
3. Add that folder to your `PATH`:
   - Start menu -> search "environment variables" -> open
     **"Edit the system environment variables"**.
   - Click **Environment Variables...**
   - Under **System variables**, select **Path** -> **Edit** -> **New**,
     and paste `C:\Program Files\Tesseract-OCR`.
   - Click OK on all dialogs.
4. Close and reopen Command Prompt, then verify:
   ```bat
   tesseract --version
   ```

**Step 3 — Install poppler (needed to render PDFs for OCR)**

1. Download the latest poppler release zip from
   <https://github.com/oschwartz10612/poppler-windows/releases>
2. Extract it somewhere permanent, e.g. `C:\poppler`.
3. Inside, find the `bin` folder (e.g.
   `C:\poppler\poppler-24.08.0\Library\bin`).
4. Add that `bin` folder to your `PATH` using the same steps as Step 2.3.
5. Close and reopen Command Prompt, then verify:
   ```bat
   pdftoppm -h
   ```

**Step 4 — Get the project code**

Either download the repository as a ZIP from GitHub (green **Code** button
-> **Download ZIP**) and extract it, **or** install Git and clone it:
```bat
git clone https://github.com/ThirdPartyThinker/EOB-Text-Extractor.git
```

**Step 5 — Install the Python dependencies**

In Command Prompt, change into the project folder and install:
```bat
cd C:\path\to\EOB-Text-Extractor
python -m pip install -r requirements.txt
```

**Step 6 — Confirm everything works**

```bat
python -m pytest
```
All 7 tests should pass (this uses synthetic data only — no real PHI).

### Part B — Processing your EOBs (do this each time)

**Step 1 — Create input and output folders**

Inside the project folder, make two folders. You can do this in File
Explorer, or in Command Prompt:
```bat
cd C:\path\to\EOB-Text-Extractor
mkdir eobs_in
mkdir eobs_out
```

**Step 2 — Put your EOB PDFs into the input folder**

Copy or drag your EOB PDF files into the `eobs_in` folder. You can add as
many as you like. Filenames are preserved, so `claim_smith.pdf` becomes
`claim_smith.txt`.

**Step 3 — Run the batch processor**

```bat
cd C:\path\to\EOB-Text-Extractor
python run_batch.py --input eobs_in --output eobs_out
```

You will see a HIPAA notice, then one log line per file showing the
filename and whether `pdfplumber` or `ocr` was used. Example:
```
INFO Extracted claim_smith.pdf via pdfplumber (2 pages, 1843 chars, 0.04s)
INFO Wrote claim_smith.txt and claim_smith.json
```

**Step 4 — Collect your results**

Open the `eobs_out` folder. For every `input.pdf` you will find:
- `input.txt`  — the extracted plain text
- `input.json` — metadata only (page count, method, timing — **no PHI**)

Open the `.txt` files in Notepad or any text editor.

**Step 5 (optional) — Tune OCR for scanned PDFs**

If a scanned PDF was not OCR'd (or a text PDF was OCR'd unnecessarily),
adjust the threshold — the average characters per page below which OCR
kicks in (default 50):
```bat
python run_batch.py --input eobs_in --output eobs_out --ocr-threshold 80
```

**Step 6 (optional) — Process a single file in Python**

```bat
python
```
```python
>>> from eob_extract import extract_text, extract_eob_fields
>>> text, metadata = extract_text(r"C:\path\to\one_eob.pdf")
>>> print(metadata)
>>> print(extract_eob_fields(text))
>>> exit()
```

### Troubleshooting (Windows)

| Symptom | Fix |
|---------|-----|
| `'python' is not recognized` | Python was installed without "Add to PATH". Re-run the installer and check that box. |
| `tesseract is not installed or it's not in your PATH` | Redo Step 2.3; reopen Command Prompt so the new `PATH` takes effect. |
| `Unable to get page count. Is poppler installed and in PATH?` | Redo Step 3.4; reopen Command Prompt. |
| Scanned PDF produced an almost-empty `.txt` | OCR may have failed — confirm `tesseract --version` works, then re-run. |

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
