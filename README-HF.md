---
title: NERVE Trading API
emoji: 🧠
colorFrom: blue
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# NERVE - Agentic Brokerage OS API

AI-powered trading intelligence and safety layer built with FastAPI and Groq.

## Features

- **Pre-Trade Sentinel**: Blocks risky trades in <50ms
- **Strategy Engine**: Natural language to backtested trading strategies
- **RAG Journaling**: AI-powered trade autopsies with market context
- **Intelligence Layer**: Multi-agent market analysis

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/sentinel/check` - Pre-trade risk check
- `POST /api/strategy/generate` - Generate trading strategy
- `POST /api/journal/autopsy` - Generate trade autopsy
- `POST /api/intelligence/gather` - Gather market intelligence
- `GET /api/market/{symbol}` - Get market data

## Environment Variables

Set these in your Hugging Face Space secrets:

- `GROQ_API_KEY` - Your Groq API key (required)

## Built With

- FastAPI
- Groq (LLaMA 3.3 70B)
- yfinance
- LangGraph
