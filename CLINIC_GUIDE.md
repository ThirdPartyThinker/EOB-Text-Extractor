# Dental Clinic Guide — EOB Text Extractor

This guide is written for clinic staff. It explains, in plain language, how
to set up the tool once on a Windows computer and then use it every day to
turn EOB PDFs into text files. No programming experience is needed.

> **This is the guide to follow for real EOBs.** Ignore the Google Colab
> and testing sections in `README.md` — those are for software developers
> only.

---

## ⚠️ Before you start — HIPAA

Real EOBs contain Protected Health Information (PHI).

- Install and run this tool **only on a clinic computer that is part of
  your HIPAA-compliant environment** (disk encryption, password/login
  controls, and your normal IT safeguards).
- **Do not** use Google Colab, personal laptops, or home computers for
  real EOBs.
- The tool works **fully offline**. It never sends EOB data over the
  internet. You can disconnect from the network while processing if your
  IT policy prefers that.
- Keep the input and output folders inside your normal secured/backed-up
  clinic storage.

---

## Part 1 — One-time setup

Do this **once** on the clinic computer. Ask your IT person if you do not
have permission to install software.

The **installer does most of the work for you.** You will: install Python,
download the program, run the installer, and then — only if the installer
asks for it — install the two OCR tools.

### Step 1: Install Python

1. Open a web browser and go to:
   <https://www.python.org/downloads/windows/>
2. Click the yellow **"Download Python 3.x"** button at the top.
3. Open the downloaded file to start the installer.
4. **IMPORTANT:** On the first screen, tick the checkbox at the bottom
   that says **"Add python.exe to PATH"**.
5. Click **"Install Now"** and wait for it to finish. Click **Close**.

### Step 2: Download the EOB Text Extractor program

1. Go to:
   <https://github.com/ThirdPartyThinker/EOB-Text-Extractor>
2. Click the green **"Code"** button, then **"Download ZIP"**.
3. Right-click the downloaded ZIP and choose **Extract All**.
4. Move the extracted `EOB-Text-Extractor` folder somewhere easy to find
   inside your secured clinic storage — for example your Documents folder.

### Step 3: Run the installer

1. Open the `EOB-Text-Extractor` folder in File Explorer.
2. Double-click the file named **`install_windows.bat`** — this is the
   installer.
3. A black window opens and runs the guided setup automatically. It will:
   - install the program's components,
   - create the `eobs_in` and `eobs_out` folders for you,
   - run a quick self-test on fake data,
   - check whether the OCR tools (Tesseract and poppler) are present.
4. Read the summary at the bottom of the window:
   - **"SETUP COMPLETE"** — everything is ready. **Skip Step 4** and go
     straight to Part 2.
   - **"SETUP FINISHED WITH ... ITEM(S) NEEDING ATTENTION"** — the
     installer prints a numbered list of exactly what is missing. If it
     mentions **Tesseract** or **poppler**, do Step 4. For anything else,
     follow the on-screen instructions.
5. Press a key to close the window.

> If Windows shows a blue "Windows protected your PC" box, click
> **More info** -> **Run anyway**. The file is a small text script you can
> open and read in Notepad.

### Step 4: Install the OCR tools — only if the installer asked for it

The OCR tools are needed **only for scanned/image EOBs**. If the installer
said everything was complete, you do not need this step at all.

**4a. Install Tesseract**

1. Go to: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Download the **64-bit** installer (look for `tesseract-ocr-w64-setup`).
3. Run it, accept the defaults, and finish. It installs to
   `C:\Program Files\Tesseract-OCR`.

**4b. Install poppler**

1. Go to:
   <https://github.com/oschwartz10612/poppler-windows/releases>
2. Download the newest `Release-xx.xx.x-0.zip` file.
3. Right-click the ZIP, choose **Extract All**, and extract it to
   `C:\poppler`.

**4c. Tell Windows where they are (set the PATH)**

1. Click the Start menu, type **environment variables**, and open
   **"Edit the system environment variables"**.
2. Click the **Environment Variables...** button.
3. In the lower box (**System variables**), click **Path**, then **Edit**.
4. Click **New** and type:
   `C:\Program Files\Tesseract-OCR`
5. Click **New** again and type the path to poppler's `bin` folder. It
   looks like:
   `C:\poppler\poppler-24.08.0\Library\bin`
   (Open `C:\poppler` in File Explorer to find the exact folder name, then
   go into `Library\bin`.)
6. Click **OK** on every window to save.

**4d. Run the installer again**

Double-click **`install_windows.bat`** once more. It should now say
**"SETUP COMPLETE"**. If it still lists a problem, restart the computer
and run the installer again.

**Setup is now finished.** You only do Part 1 once.

---

## Part 2 — Using the tool every day

### Step 1: Put EOB PDFs into the input folder

1. Open the `EOB-Text-Extractor` folder.
2. Open the folder named **`eobs_in`** (the installer created it for you
   in Part 1).
3. Copy or drag the EOB PDF files you want to convert into `eobs_in`.
   You can add as many as you like.

### Step 2: Run the converter

1. In the `EOB-Text-Extractor` folder, double-click
   **`run_extractor.bat`**.
2. A black window opens and shows the HIPAA notice, then a line for each
   PDF as it is processed. It finishes with
   **"Done. Your text files are in the eobs_out folder."**
3. Press a key to close the window.

### Step 3: Get your text files

1. Open the **`eobs_out`** folder inside `EOB-Text-Extractor`.
2. For each PDF you put in, you will find two files:
   - **`<name>.txt`** — the EOB text. Double-click to open in Notepad.
   - **`<name>.json`** — a small technical summary (page count, timing).
     It contains **no patient information** and can be ignored.
3. The `.txt` files keep the original names. `claim_jones.pdf` becomes
   `claim_jones.txt`.

### Step 4: Clear the folders for next time (recommended)

After you have saved the text files where they belong, move the processed
PDFs out of `eobs_in` and the results out of `eobs_out`, so the next batch
starts clean. Store them according to your clinic's records policy.

---

## What the tool does automatically

- **Normal (digital) EOB PDFs:** the text is read directly — fast.
- **Scanned or image EOB PDFs:** the tool automatically switches to OCR
  (optical character recognition) to read the text from the image. This is
  slower and slightly less accurate, so always double-check important
  numbers against the original PDF.

---

## If something goes wrong

| What you see | What to do |
|--------------|------------|
| The black window flashes and closes instantly | Right-click the `.bat` file -> **Edit** is not needed; instead open Command Prompt in the folder and run it so the error stays visible. Contact IT with the message. |
| "`python` is not recognized" | Python was installed without the PATH checkbox. Redo **Part 1, Step 1** and be sure to tick **"Add python.exe to PATH"**. |
| "tesseract is not installed or it's not in your PATH" | Do **Part 1, Step 4** (install Tesseract and set its PATH), then restart the computer. |
| "Unable to get page count. Is poppler installed and in PATH?" | Do **Part 1, Step 4** (install poppler and set its PATH), then restart the computer. |
| A scanned EOB produced an almost-empty `.txt` file | The scan quality may be poor. Re-scan the original at higher quality, or check that Tesseract installed correctly. |
| Nothing happens / "No PDF files found" | Make sure your PDFs are actually inside the `eobs_in` folder and end in `.pdf`. |

For anything else, contact your IT support and share the text shown in the
black window.

---

## Quick reference

| Task | What to do |
|------|------------|
| First-time setup | Do **Part 1** once |
| Convert EOBs | Put PDFs in `eobs_in`, double-click `run_extractor.bat` |
| Find results | Open the `eobs_out` folder |
| Where it's safe to run | A HIPAA-compliant clinic computer only |
