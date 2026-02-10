# Configuration Guide

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
GROQ_API_KEY=gsk_your_actual_key_here

# Optional: Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=us-west1-gcp
PINECONE_INDEX=trading-memory

# Optional: News & Sentiment
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key

# System Settings
SENTINEL_LATENCY_MS=50
PERCEPTION_TIMEOUT_MS=200
LOG_LEVEL=INFO

# Trading Defaults
MAX_POSITION_SIZE=10000
MAX_DAILY_LOSS=5000
MAX_LEVERAGE=2.0
ENABLE_KILL_SWITCH=true
DEFAULT_PAPER_TRADING=true
```

## User Constitution

Customize your trading rules by creating `config/my_constitution.json`:

```json
{
  "max_position_size": 10000,
  "max_daily_loss": 5000,
  "max_leverage": 1.5,
  "min_time_between_trades": 60,
  "max_trades_per_day": 10,
  "block_after_loss_streak": 3,
  "block_on_tilt": true,
  "require_cooldown": true,
  "cooldown_duration_minutes": 30,
  "allowed_symbols": ["AAPL", "MSFT", "GOOGL"],
  "blocked_symbols": ["MEME"],
  "trading_hours_only": true,
  "strategies_require_backtest": true,
  "min_backtest_trades": 30,
  "min_sharpe_ratio": 1.0,
  "enable_kill_switch": true
}
```

Load in code:
```python
import json
from src.core.state import UserConstitution

with open("config/my_constitution.json") as f:
    data = json.load(f)
    constitution = UserConstitution(**data)
```

## Groq API Setup

1. Get API key from: https://console.groq.com/keys
2. Models available:
   - `llama-3.2-90b-vision-preview` (vision + text, for perception)
   - `llama-3.1-70b-versatile` (text only, for strategy generation)
   - `llama-3.1-8b-instant` (fast, for sentinel checks)

## Pinecone Setup (Optional)

1. Create account: https://www.pinecone.io/
2. Create index:
   ```python
   import pinecone
   
   pinecone.init(api_key="YOUR_KEY", environment="us-west1-gcp")
   pinecone.create_index("trading-memory", dimension=384)
   ```

## Logging Configuration

Logs are saved to `logs/brokerage_os_{time}.log` with 7-day retention.

Customize in code:
```python
from loguru import logger

logger.add(
    "logs/custom_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"  # Change to DEBUG for verbose output
)
```

## Performance Tuning

### Reduce Latency
- Use `llama-3.1-8b-instant` for sentinel (fastest model)
- Pre-warm connections to Groq API on startup
- Cache UI perception results for 1-2 seconds

### Improve Accuracy
- Use `llama-3.2-90b-vision-preview` for perception (best vision model)
- Increase screenshot resolution (trade latency for detail)
- Fine-tune perception prompts for your specific broker UI

### Scale for Production
- Implement request pooling for Groq API
- Use Redis for distributed state management
- Deploy vector DB cluster (Pinecone/Weaviate)
