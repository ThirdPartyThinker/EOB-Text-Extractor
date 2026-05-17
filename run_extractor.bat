@echo off
REM ==================================================================
REM  EOB Text Extractor - convert EOB PDFs to text files
REM  Reads PDFs from the "eobs_in" folder and writes results to
REM  "eobs_out". See CLINIC_GUIDE.md, Part 2.
REM ==================================================================
cd /d "%~dp0"

if not exist "eobs_in"  mkdir "eobs_in"
if not exist "eobs_out" mkdir "eobs_out"

echo.
echo Converting EOB PDFs from the "eobs_in" folder...
echo.

python run_batch.py --input eobs_in --output eobs_out
if errorlevel 1 (
    echo.
    echo ------------------------------------------------------------
    echo  Something went wrong. See the message above and
    echo  CLINIC_GUIDE.md, section "If something goes wrong".
    echo ------------------------------------------------------------
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done. Your text files are in the "eobs_out" folder.
echo ============================================================
echo.
pause
