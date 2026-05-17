@echo off
REM ==================================================================
REM  EOB Text Extractor - one-time Windows setup
REM  Installs the Python components the tool needs.
REM  (Python, Tesseract, and poppler must already be installed - see
REM   CLINIC_GUIDE.md, Part 1, Steps 1-4.)
REM ==================================================================
cd /d "%~dp0"

echo.
echo Installing EOB Text Extractor components...
echo.

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ------------------------------------------------------------
    echo  Setup FAILED. Python may not be installed correctly.
    echo  See CLINIC_GUIDE.md, Part 1, Step 1.
    echo ------------------------------------------------------------
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Setup complete. You can now use run_extractor.bat.
echo ============================================================
echo.
pause
