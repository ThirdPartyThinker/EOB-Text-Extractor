@echo off
REM ==================================================================
REM  EOB Text Extractor - one-time Windows setup
REM  Runs the guided setup program (setup_eob.py): installs the Python
REM  components, checks the OCR tools, creates the working folders,
REM  and runs a self-test.
REM
REM  Python must already be installed - see CLINIC_GUIDE.md, Part 1,
REM  Step 1. Tesseract and poppler are only needed for scanned EOBs.
REM ==================================================================
cd /d "%~dp0"

python setup_eob.py
if errorlevel 1 (
    echo.
    echo ------------------------------------------------------------
    echo  Setup reported items that need attention - see the list
    echo  above and CLINIC_GUIDE.md.
    echo ------------------------------------------------------------
)

echo.
pause
