@echo off
REM Quick launch script for Agentic Brokerage OS Dashboard
REM Makes it easy for judges to run the demo

echo ========================================
echo   Agentic Brokerage OS Dashboard
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found
    echo [*] Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [*] Installing dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo [*] Launching dashboard...
echo [*] Open your browser and go to: http://localhost:8501
echo.

streamlit run dashboard.py

pause
