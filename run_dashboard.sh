#!/bin/bash
# Quick launch script for Agentic Brokerage OS Dashboard
# Makes it easy for judges to run the demo

echo "========================================"
echo "  Agentic Brokerage OS Dashboard"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "[!] Virtual environment not found"
    echo "[*] Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "[*] Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo ""
echo "[*] Launching dashboard..."
echo "[*] Open your browser and go to: http://localhost:8501"
echo ""

streamlit run dashboard.py
