@echo off
cd /d D:\comp\zerodha
call .venv\Scripts\activate.bat
pip install uvicorn fastapi yfinance python-dotenv python-multipart --quiet
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
pause
