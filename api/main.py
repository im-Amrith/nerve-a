"""
FastAPI Backend for Agentic Brokerage OS
Exposes all AI engines via REST API for React frontend
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
from dotenv import load_dotenv

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engines.pre_trade_sentinel import PreTradeSentinel
from src.engines.strategy_engine import StrategyEngine
from src.engines.rag_journal import RAGJournal
from src.engines.retail_intelligence import RetailIntelligenceLayer
from src.core.state import TradeIntent, UserConstitution

load_dotenv()

# Global engine instances
sentinel = None
strategy_engine = None
rag_journal = None
intelligence_layer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize engines on startup"""
    global sentinel, strategy_engine, rag_journal, intelligence_layer
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable required")
    
    # Initialize Pre-Trade Sentinel with default constitution
    default_constitution = UserConstitution(
        max_position_size_pct=10.0,
        max_daily_loss_pct=5.0,
        blocked_symbols=[],
        trading_hours_only=True,
        require_stop_loss=False,
        max_leverage=1.0,
        min_cash_reserve_pct=20.0,
        enable_kill_switch=True,
        cooldown_after_loss_streak=3,
        max_trades_per_day=10
    )
    sentinel = PreTradeSentinel(groq_api_key, default_constitution)
    
    # Initialize other engines
    strategy_engine = StrategyEngine(groq_api_key)
    rag_journal = RAGJournal(groq_api_key)
    intelligence_layer = RetailIntelligenceLayer(groq_api_key)
    
    yield
    
    # Cleanup if needed
    pass

app = FastAPI(
    title="Agentic Brokerage OS API",
    description="AI-powered trading intelligence and safety layer",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for React frontend (local dev + Vercel + HuggingFace)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.hf.space",
    ],
    allow_origin_regex=r"https://.*\.(vercel\.app|hf\.space)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================== Request/Response Models ==================

class TradeCheckRequest(BaseModel):
    symbol: str
    action: str  # "buy" or "sell"
    quantity: int
    price: float
    order_type: str = "market"
    rationale: Optional[str] = None

class PortfolioState(BaseModel):
    cash: float = 100000.0
    positions: Dict[str, Dict] = {}

class StrategyRequest(BaseModel):
    strategy_description: str
    backtest_symbol: str = "SPY"

class JournalRequest(BaseModel):
    symbol: str
    action: str
    quantity: int
    entry_price: float
    exit_price: float
    rationale: str

class IntelligenceRequest(BaseModel):
    symbol: str

class StockPriceRequest(BaseModel):
    symbol: str


# ================== API Endpoints ==================

@app.get("/")
async def root():
    return {
        "name": "Agentic Brokerage OS",
        "version": "1.0.0",
        "status": "running",
        "engines": ["sentinel", "strategy", "journal", "intelligence"]
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# === Pre-Trade Sentinel ===
@app.post("/api/sentinel/check")
async def check_trade(request: TradeCheckRequest):
    """Run trade through Pre-Trade Sentinel safety checks"""
    portfolio = PortfolioState()
    
    intent = TradeIntent(
        symbol=request.symbol.upper(),
        action=request.action.lower(),
        quantity=request.quantity,
        price=request.price,
        order_type=request.order_type,
        timestamp=datetime.now(),
        natural_language_prompt=request.rationale
    )
    
    portfolio_dict = {
        "cash": portfolio.cash,
        "positions": portfolio.positions,
        "total_value": portfolio.cash + sum(
            p.get("value", 0) for p in portfolio.positions.values()
        )
    }
    
    # Run blocking call in thread pool to avoid blocking event loop
    result = await asyncio.to_thread(sentinel.check_trade, intent, portfolio_dict)
    
    return {
        "approved": result.approved,
        "risk_score": result.risk_score,
        "reasoning": result.reasoning,
        "violated_rules": result.violated_rules,
        "recommended_action": result.recommended_action,
        "latency_ms": result.inference_time_ms
    }


# === Strategy Engine ===
@app.post("/api/strategy/generate")
async def generate_strategy(request: StrategyRequest):
    """Generate and backtest an AI trading strategy"""
    try:
        result = await asyncio.to_thread(
            strategy_engine.generate_strategy,
            natural_language_prompt=request.strategy_description,
            backtest_symbol=request.backtest_symbol
        )
        return {
            "success": True,
            "strategy_code": result.generated_code,
            "backtest_results": result.backtest_results or {},
            "reasoning": result.description
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "strategy_code": "",
            "backtest_results": {},
            "reasoning": f"Error: {str(e)}"
        }


# === RAG Journal ===
@app.post("/api/journal/autopsy")
async def generate_autopsy(request: JournalRequest):
    """Generate AI autopsy report for a trade"""
    try:
        from groq import Groq
        
        # Calculate P&L
        pnl = (request.exit_price - request.entry_price) * request.quantity
        if request.action.lower() == 'sell':
            pnl = -pnl
        pnl_pct = ((request.exit_price - request.entry_price) / request.entry_price) * 100
        
        # Get market context using yfinance
        import yfinance as yf
        ticker = yf.Ticker(request.symbol)
        ticker_info = ticker.info
        
        # Generate autopsy using Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = f"""You are a professional trading analyst. Generate a detailed "Trade Autopsy" report for this trade.

TRADE DETAILS:
- Symbol: {request.symbol}
- Action: {request.action.upper()}
- Quantity: {request.quantity}
- Entry Price: ${request.entry_price}
- Exit Price: ${request.exit_price}
- P&L: ${pnl:.2f} ({pnl_pct:.2f}%)
- User's Rationale: "{request.rationale}"

CURRENT MARKET INFO:
- Current Price: ${ticker_info.get('currentPrice', ticker_info.get('regularMarketPrice', 'N/A'))}
- 52-Week High: ${ticker_info.get('fiftyTwoWeekHigh', 'N/A')}
- 52-Week Low: ${ticker_info.get('fiftyTwoWeekLow', 'N/A')}
- Company: {ticker_info.get('longName', request.symbol)}

Analyze this trade and provide:
1. A brief market context summary
2. Detailed analysis of the trade execution
3. 3-4 specific lessons learned

Return your response as valid JSON (no markdown, no code blocks):
{{"market_context": "summary here", "analysis": "detailed analysis here", "lessons_learned": ["lesson 1", "lesson 2", "lesson 3"]}}"""

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
        )
        
        import json
        raw = response.choices[0].message.content.strip()
        
        # Clean up response
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        
        # Find JSON in response
        start_idx = raw.find('{')
        end_idx = raw.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            raw = raw[start_idx:end_idx]
        
        result = json.loads(raw)
        result['pnl'] = pnl
        result['pnl_pct'] = pnl_pct
        result['symbol'] = request.symbol
        
        return {
            "success": True,
            "autopsy": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "autopsy": None
        }

@app.get("/api/journal/insights")
async def get_insights(timeframe_days: int = 30):
    """Get AI-generated trading insights"""
    try:
        insights = rag_journal.generate_insights(timeframe_days)
        return {"success": True, "insights": insights}
    except Exception as e:
        return {"success": False, "error": str(e), "insights": None}

@app.get("/api/journal/query")
async def query_trades(query: str, top_k: int = 5):
    """Query past trades using semantic search"""
    try:
        results = rag_journal.query_past_trades(query, top_k)
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e), "results": []}


# === Retail Intelligence ===
@app.post("/api/intelligence/gather")
async def gather_intelligence(request: IntelligenceRequest):
    """Gather multi-agent intelligence for a symbol"""
    try:
        result = await intelligence_layer.gather_intelligence(request.symbol.upper())
        
        # Make result JSON serializable
        serializable_result = {
            "symbol": result.get("symbol"),
            "timestamp": result.get("timestamp").isoformat() if result.get("timestamp") else None,
            "elapsed_seconds": result.get("elapsed_seconds"),
            "synthesis": result.get("synthesis"),
            "agent_count": result.get("agent_count"),
            "raw_intelligence": []
        }
        
        # Process raw intelligence
        for intel in result.get("raw_intelligence", []):
            clean_intel = {}
            for key, value in intel.items():
                if isinstance(value, datetime):
                    clean_intel[key] = value.isoformat()
                elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    clean_intel[key] = value
                else:
                    clean_intel[key] = str(value)
            serializable_result["raw_intelligence"].append(clean_intel)
        
        return {"success": True, "intelligence": serializable_result}
    except Exception as e:
        return {"success": False, "error": str(e), "intelligence": None}


# === Stock Data ===
@app.get("/api/stock/{symbol}")
async def get_stock_price(symbol: str):
    """Get current stock price and info"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        hist = ticker.history(period="5d")
        
        current_price = None
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
        elif 'regularMarketPrice' in info:
            current_price = info['regularMarketPrice']
        elif 'previousClose' in info:
            current_price = info['previousClose']
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "price": current_price,
            "name": info.get("shortName", info.get("longName", symbol)),
            "change": info.get("regularMarketChange"),
            "changePercent": info.get("regularMarketChangePercent"),
            "volume": info.get("regularMarketVolume"),
            "marketCap": info.get("marketCap"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow")
        }
    except Exception as e:
        return {"success": False, "error": str(e), "symbol": symbol}


# === Watchlist ===
@app.get("/api/watchlist")
async def get_watchlist():
    """Get default watchlist with prices"""
    symbols = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "META", "AMZN", "SPY"]
    watchlist = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                current = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                change = current - prev
                change_pct = (change / prev * 100) if prev else 0
                
                watchlist.append({
                    "symbol": symbol,
                    "price": round(current, 2),
                    "change": round(change, 2),
                    "changePercent": round(change_pct, 2)
                })
        except:
            pass
    
    return {"success": True, "watchlist": watchlist}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
