"""
Contextual RAG Journaling (FR3): Trade autopsy with market context.
Scrapes real-time news/sentiment at trade closure to improve future discipline.
"""

import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import requests
from groq import Groq
from loguru import logger
import pandas as pd

from ..core.state import TradeExecution, MarketContext


class RAGJournal:
    """
    Captures market context at trade execution and generates "Trade Autopsy" reports.
    Helps users understand why trades succeeded/failed relative to market conditions.
    """
    
    def __init__(
        self, 
        groq_api_key: str,
        news_api_key: Optional[str] = None,
        vector_db_client=None
    ):
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        self.news_api_key = news_api_key
        self.vector_db = vector_db_client
        self.journal_entries: List[Dict] = []
        
    def capture_context(
        self, 
        trade: TradeExecution,
        fetch_news: bool = True,
        fetch_sentiment: bool = True
    ) -> MarketContext:
        """
        Capture comprehensive market context at trade execution time.
        
        Args:
            trade: The executed trade
            fetch_news: Whether to fetch real-time news
            fetch_sentiment: Whether to analyze sentiment
            
        Returns:
            MarketContext with all available data
        """
        logger.info(f"Capturing market context for trade: {trade.trade_id}")
        
        symbol = trade.intent.symbol
        
        # Simulate fetching current market data (in production, use real API)
        price_data = self._fetch_price_data(symbol)
        
        # Fetch real-time news
        news_headlines = []
        if fetch_news and self.news_api_key:
            news_headlines = self._fetch_news(symbol)
        
        # Analyze sentiment
        sentiment_score = None
        if fetch_sentiment:
            sentiment_score = self._analyze_sentiment(news_headlines)
        
        # Calculate technical indicators
        technicals = self._calculate_technicals(symbol)
        
        context = MarketContext(
            timestamp=datetime.now(),
            symbol=symbol,
            current_price=price_data.get("price", 0.0),
            day_high=price_data.get("high", 0.0),
            day_low=price_data.get("low", 0.0),
            volume=price_data.get("volume", 0),
            rsi=technicals.get("rsi"),
            macd=technicals.get("macd"),
            moving_averages=technicals.get("ma"),
            news_headlines=news_headlines,
            sentiment_score=sentiment_score,
            market_regime=self._detect_market_regime(symbol)
        )
        
        logger.success(f"Context captured: {len(news_headlines)} news items, sentiment={sentiment_score}")
        
        return context
    
    def generate_autopsy(
        self, 
        trade: TradeExecution,
        context: MarketContext,
        user_notes: Optional[str] = None
    ) -> str:
        """
        Generate "Trade Autopsy" - post-mortem analysis comparing intent vs reality.
        
        Args:
            trade: Executed trade
            context: Market context at execution
            user_notes: Optional user annotations
            
        Returns:
            Detailed autopsy report
        """
        logger.info(f"Generating autopsy for trade: {trade.trade_id}")
        
        # Build context for LLM
        prompt = f"""You are a professional trading psychologist and analyst. Generate a "Trade Autopsy" report.

TRADE DETAILS:
- Action: {trade.intent.action.upper()}
- Symbol: {trade.intent.symbol}
- Quantity: {trade.intent.quantity}
- Intent Price: ${trade.intent.price or 'Market'}
- Actual Fill: ${trade.actual_fill_price or 'N/A'}
- Order Type: {trade.intent.order_type}
- Status: {trade.status}
- Timestamp: {trade.execution_timestamp}

USER INTENT:
"{trade.intent.natural_language_prompt or 'No explicit reason provided'}"

MARKET CONTEXT AT EXECUTION:
- Price: ${context.current_price:.2f} (Day Range: ${context.day_low:.2f} - ${context.day_high:.2f})
- RSI: {context.rsi or 'N/A'}
- Sentiment Score: {context.sentiment_score or 'N/A'} (-1 to +1)
- Market Regime: {context.market_regime or 'Unknown'}

NEWS HEADLINES:
{chr(10).join(f"- {h}" for h in context.news_headlines[:5]) if context.news_headlines else "No news available"}

USER NOTES:
{user_notes or 'None'}

Generate a structured autopsy report with these sections:

1. EXECUTION QUALITY (1-10 score)
   - Was entry price favorable?
   - Was timing appropriate given market conditions?

2. INTENT VS REALITY
   - Did market conditions support the user's thesis?
   - Were there contradicting signals the user missed?

3. BEHAVIORAL ANALYSIS
   - Signs of emotional trading (FOMO, revenge trading, overconfidence)?
   - Alignment with disciplined trading practice?

4. LESSONS LEARNED
   - What went well?
   - What could be improved?
   - Specific actionable takeaways

5. FUTURE GUARDRAILS
   - Suggested rule additions to prevent similar mistakes
   - Recommended strategy adjustments

Keep it concise but insightful. Be honest but constructive."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            
            autopsy = response.choices[0].message.content
            
            # Store in journal
            journal_entry = {
                "trade_id": trade.trade_id,
                "timestamp": datetime.now(),
                "autopsy": autopsy,
                "context": context.dict(),
                "user_notes": user_notes
            }
            self.journal_entries.append(journal_entry)
            
            # Store in vector DB for future RAG retrieval
            if self.vector_db:
                self._store_in_vector_db(journal_entry)
            
            logger.success(f"Autopsy generated for trade {trade.trade_id}")
            
            return autopsy
            
        except Exception as e:
            logger.error(f"Autopsy generation failed: {e}")
            return f"Failed to generate autopsy: {e}"
    
    def query_past_trades(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Query past trade journal using RAG.
        
        Args:
            query: Natural language query (e.g., "show me trades where I ignored RSI")
            top_k: Number of similar trades to retrieve
            
        Returns:
            List of relevant journal entries
        """
        logger.info(f"Querying journal: '{query}'")
        
        if self.vector_db:
            # Use vector DB similarity search
            results = self._vector_search(query, top_k)
        else:
            # Fallback: keyword-based search
            results = self._keyword_search(query, top_k)
        
        return results
    
    def generate_insights(self, timeframe_days: int = 30) -> str:
        """
        Generate high-level insights from recent trading history.
        
        Args:
            timeframe_days: Number of days to analyze
            
        Returns:
            Insights report
        """
        cutoff = datetime.now() - timedelta(days=timeframe_days)
        recent_entries = [
            e for e in self.journal_entries
            if e["timestamp"] > cutoff
        ]
        
        if not recent_entries:
            return "No recent trades to analyze."
        
        # Aggregate insights using LLM
        summary = f"Analyzing {len(recent_entries)} trades from past {timeframe_days} days...\n\n"
        
        # Extract patterns
        autopsies = [e["autopsy"] for e in recent_entries]
        combined = "\n\n---\n\n".join(autopsies[:10])  # Limit to avoid token overflow
        
        prompt = f"""Analyze these trade autopsies and identify patterns:

{combined}

Provide:
1. RECURRING MISTAKES (top 3)
2. STRONGEST PERFORMING SETUPS (top 2)
3. EMOTIONAL TRIGGERS DETECTED
4. RECOMMENDED RULE CHANGES

Be specific and actionable."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1000
            )
            
            insights = response.choices[0].message.content
            return summary + insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return summary + f"Failed to generate insights: {e}"
    
    def _fetch_price_data(self, symbol: str) -> Dict:
        """Fetch current price data using Yahoo Finance."""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price from various possible fields
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('ask') or 
                info.get('bid') or
                0
            )
            
            if current_price > 0:
                return {
                    "price": current_price,
                    "high": info.get('dayHigh', current_price * 1.02),
                    "low": info.get('dayLow', current_price * 0.98),
                    "volume": info.get('volume', 0),
                    "market_cap": info.get('marketCap', 0),
                    "pe_ratio": info.get('trailingPE', 0),
                    "52w_high": info.get('fiftyTwoWeekHigh', 0),
                    "52w_low": info.get('fiftyTwoWeekLow', 0)
                }
            else:
                # Fallback to historical data
                hist = ticker.history(period="1d")
                if not hist.empty:
                    return {
                        "price": float(hist['Close'].iloc[-1]),
                        "high": float(hist['High'].iloc[-1]),
                        "low": float(hist['Low'].iloc[-1]),
                        "volume": int(hist['Volume'].iloc[-1])
                    }
                    
        except Exception as e:
            logger.warning(f"Yahoo Finance fetch failed for {symbol}: {e}")
        
        # Fallback mock data if API fails
        logger.warning(f"Using mock data for {symbol}")
        import random
        base_price = 100 + random.uniform(-10, 10)
        return {
            "price": base_price,
            "high": base_price * 1.05,
            "low": base_price * 0.95,
            "volume": random.randint(1000000, 5000000)
        }
    
    def _fetch_news(self, symbol: str) -> List[str]:
        """Fetch real-time news headlines using yfinance (free)."""
        try:
            import yfinance as yf
            
            # Try with exchange suffixes for non-US stocks
            symbols_to_try = [symbol]
            if '.' not in symbol:
                symbols_to_try.extend([f"{symbol}.NS", f"{symbol}.BO"])
            
            for sym in symbols_to_try:
                try:
                    ticker = yf.Ticker(sym)
                    news = ticker.news
                    if news:
                        headlines = [article.get("title", "") for article in news[:5]]
                        return [h for h in headlines if h]  # Filter empty
                except:
                    continue
            
            # Fallback to NewsAPI if configured and yfinance has no news
            if self.news_api_key:
                return self._fetch_news_from_newsapi(symbol)
            
            return []
                
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")
            return []
    
    def _fetch_news_from_newsapi(self, symbol: str) -> List[str]:
        """Fallback to NewsAPI.org if configured."""
        try:
            url = f"https://newsapi.org/v2/everything"
            params = {
                "q": symbol,
                "apiKey": self.news_api_key,
                "pageSize": 5,
                "sortBy": "publishedAt",
                "language": "en"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                headlines = [a["title"] for a in articles]
                return headlines
        except Exception as e:
            logger.warning(f"NewsAPI fallback failed: {e}")
        
        return []
    
    def _analyze_sentiment(self, headlines: List[str]) -> Optional[float]:
        """Analyze sentiment of news headlines."""
        if not headlines:
            return None
        
        combined_text = " ".join(headlines)
        
        # Simple sentiment analysis using LLM
        try:
            prompt = f"""Analyze the sentiment of these news headlines and return a score from -1 (very negative) to +1 (very positive):

Headlines:
{combined_text}

Respond with ONLY a number between -1 and 1, nothing else."""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast model for quick sentiment
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=10
            )
            
            score_str = response.choices[0].message.content.strip()
            score = float(score_str)
            return max(-1.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return None
    
    def _calculate_technicals(self, symbol: str) -> Dict:
        """Calculate technical indicators (mock implementation)."""
        # In production, calculate from real price history
        import random
        return {
            "rsi": random.uniform(30, 70),
            "macd": {"value": random.uniform(-2, 2), "signal": random.uniform(-2, 2)},
            "ma": {"sma_20": 100, "sma_50": 98, "sma_200": 95}
        }
    
    def _detect_market_regime(self, symbol: str) -> str:
        """Detect current market regime (trending, ranging, volatile)."""
        # Simplified regime detection
        import random
        return random.choice(["trending", "ranging", "volatile"])
    
    def _store_in_vector_db(self, entry: Dict):
        """Store journal entry in vector database for RAG."""
        if not self.vector_db:
            return
        
        try:
            # Create embedding of autopsy text
            text = entry["autopsy"]
            entry_id = hashlib.md5(text.encode()).hexdigest()
            
            # Store with metadata
            self.vector_db.upsert(
                vectors=[{
                    "id": entry_id,
                    "values": self._create_embedding(text),
                    "metadata": {
                        "trade_id": entry["trade_id"],
                        "timestamp": entry["timestamp"].isoformat(),
                        "text": text[:500]  # Store snippet
                    }
                }]
            )
            logger.info(f"Stored entry {entry_id} in vector DB")
        except Exception as e:
            logger.error(f"Vector DB storage failed: {e}")
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create text embedding (simplified - use real embedding model in production)."""
        # In production, use a real embedding model (OpenAI, Sentence Transformers, etc.)
        import hashlib
        import random
        
        # Deterministic pseudo-embedding based on text hash
        random.seed(int(hashlib.md5(text.encode()).hexdigest(), 16))
        return [random.random() for _ in range(384)]
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict]:
        """Search vector DB for similar trades."""
        try:
            query_embedding = self._create_embedding(query)
            results = self.vector_db.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            return results.get("matches", [])
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Fallback keyword-based search."""
        keywords = query.lower().split()
        scored_entries = []
        
        for entry in self.journal_entries:
            text = entry["autopsy"].lower()
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scored_entries.append((score, entry))
        
        scored_entries.sort(reverse=True, key=lambda x: x[0])
        return [e[1] for e in scored_entries[:top_k]]
