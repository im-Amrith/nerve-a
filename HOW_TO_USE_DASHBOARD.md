# 📖 Dashboard User Guide - How to Use All Features

This guide walks you through using every functionality in the **Agentic Brokerage OS Dashboard**.

---

## 🚀 Getting Started

### Step 1: Launch the Dashboard

**Option 1 - One-Click Launch (Recommended):**
```bash
# Windows
run_dashboard.bat

# Linux/Mac
./run_dashboard.sh
```

**Option 2 - Manual Launch:**
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run dashboard
streamlit run dashboard.py
```

### Step 2: Open in Browser
The terminal will show:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Click the link or go to: **http://localhost:8501**

### Step 3: Verify Setup
At the top of the dashboard, you should see 4 metric cards:
- 🛡️ Pre-Trade Sentinel: Active
- 🧠 Strategy Engine: Ready
- 📝 RAG Journal: Logging
- 🌐 Intelligence Layer: 4 Agents

**Sidebar System Info:**
- ✓ Groq API: Configured
- ✓ News API: Configured (or ✗ Optional)
- Engines: 4/4 Active

If you see "✗ Missing" for Groq API, you need to add your API key to the `.env` file.

---

## 🛡️ Feature 1: Pre-Trade Sentinel

### What It Does
The Pre-Trade Sentinel is a kill switch that blocks risky trades in under 50 milliseconds. It checks your trade against personalized rules before execution.

### How to Use

#### Step 1: Select Feature
Click **"🛡️ Pre-Trade Sentinel"** in the sidebar radio buttons.

#### Step 2: Enter Trade Parameters

**Left Panel - "Test Trade Parameters":**

1. **Symbol** (text input)
   - Enter a stock ticker (e.g., `AAPL`, `TSLA`, `NVDA`)
   - Example: `AAPL`

2. **Quantity** (number input)
   - How many shares to trade
   - Example: `10`

3. **Action** (dropdown)
   - Select `buy` or `sell`
   - Example: `buy`

4. **Price** (number input)
   - Price per share
   - Example: `150.00`

5. Click the **🔍 Check Trade** button

#### Step 3: View Results

**Right Panel - "Sentinel Result":**

**Latency Indicator:**
- Green success box: "⚡ Latency: X.XXms (✓ Sub-50ms)"
- Shows how fast the check completed
- Target: Under 50ms (usually completes in <1ms for deterministic checks)

**Approval Decision:**
- **Green Box (✅ APPROVED):** Trade is safe to execute
  - Shows reasoning: "Low risk (0.30/1.00), all checks passed"
- **Red Box (🚫 BLOCKED):** Trade violates safety rules
  - Shows reasoning: "BLOCKED: Symbol GME is blocked"

**Metrics:**
- **Risk Score:** 0.00 to 1.00 (lower is safer)
  - 0.00-0.30: Low risk ✅
  - 0.30-0.50: Moderate risk ⚠️
  - 0.50-0.80: High risk ⚠️
  - 0.80-1.00: Extreme risk ❌
  
- **Violations:** Number of rules violated
  - 0: All checks passed
  - 1+: Shows list of violated rules below

**Violated Rules List:**
If any rules are broken, you'll see:
- "Symbol GME is blocked"
- "Position size exceeds limit: $200,000 > $10,000"
- "Outside trading hours (current: 6:00)"

### Example Tests to Try

#### Test 1: Normal Trade (Should Pass ✅)
```
Symbol: AAPL
Quantity: 10
Action: buy
Price: 150.00
```
**Expected:** ✅ APPROVED, Risk: ~0.30, Latency: <1ms

#### Test 2: Banned Symbol (Should Fail ❌)
```
Symbol: GME
Quantity: 100
Action: buy
Price: 20.00
```
**Expected:** 🚫 BLOCKED, "Symbol GME is blocked"

#### Test 3: Oversized Position (Should Fail ❌)
```
Symbol: TSLA
Quantity: 1000
Action: buy
Price: 200.00
```
**Expected:** 🚫 BLOCKED, "Position size exceeds limit"

#### Test 4: High-Risk Trade (May Pass with Warning ⚠️)
```
Symbol: NVDA
Quantity: 50
Action: buy
Price: 500.00
```
**Expected:** ✅ APPROVED but Risk: ~0.80 (caution advised)

### Understanding Risk Scores

The risk score is calculated from:
- **Rule violations** (+0.2 per violation)
- **Position size** relative to portfolio (+0.3 max)
- **Order type** (market orders +0.1)
- **Loss streak** history (+0.15 per consecutive loss)

### What to Expect

**Fast Deterministic Checks (<1ms):**
- Position size limits
- Banned symbols
- Trading hours
- Cooldown periods

**Slower LLM Checks (~500-700ms):**
- Edge cases with risk score 0.3-0.7
- Behavioral pattern analysis
- Complex rule interactions

Only borderline cases trigger the LLM for detailed reasoning.

---

## 🧠 Feature 2: Semantic Strategy Engine

### What It Does
Converts natural language trading ideas into executable Python code with automatic backtesting. No programming knowledge required!

### How to Use

#### Step 1: Select Feature
Click **"🧠 Strategy Engine"** in the sidebar.

#### Step 2: Describe Your Strategy

**Left Panel - "Natural Language Strategy":**

In the text area, describe your trading idea in plain English. Be specific about:
- **Entry conditions:** When to buy
- **Exit conditions:** When to sell
- **Indicators:** RSI, MACD, moving averages, etc.

**Example Strategies:**

**Simple RSI Strategy:**
```
Buy when RSI is below 30 (oversold).
Sell when RSI goes above 70 (overbought).
```

**MACD Crossover:**
```
Buy when MACD crosses above the signal line and volume is high.
Sell when MACD crosses below the signal line or stop loss hits 2%.
```

**Moving Average Strategy:**
```
Buy when price breaks above the 20-day moving average with increasing volume.
Sell when price drops 3% below entry or hits the 50-day moving average.
```

**Advanced Multi-Indicator:**
```
Buy when:
- RSI is between 30 and 50
- MACD histogram is positive
- Price is above 200-day MA
- Volume is 1.5x average

Sell when:
- RSI exceeds 70
- Stop loss at 5% below entry
- Take profit at 10% above entry
```

#### Step 3: Generate Strategy
Click **🚀 Generate Strategy** button.

**What Happens Next:**
1. Spinner appears: "🤖 Generating strategy with Groq LLM..."
2. LLM processes your description (3-5 seconds)
3. Generates Python code (4000-5000 characters)
4. Validates code syntax and security
5. Runs automatic backtest
6. Shows success message: "✅ Strategy generated successfully!"

#### Step 4: View Results

**Right Panel - "Generated Strategy":**

**Strategy Info:**
- **Name:** Auto-generated from your description (e.g., `buy_when_rsi_is_below`)
- **ID:** Unique identifier (UUID)

**Backtest Metrics:**
Three columns showing:

1. **Sharpe Ratio:** Risk-adjusted returns
   - \> 2.0: Excellent ✅
   - 1.0-2.0: Good ✅
   - 0.5-1.0: Acceptable ⚠️
   - < 0.5: Poor ❌

2. **Total Return:** Overall profit/loss percentage
   - Example: +15.2% or -3.5%

3. **Total Trades:** Number of trades in backtest
   - More trades = more statistical significance
   - Example: 45 trades

**View Generated Code:**
Click **"📄 View Generated Code"** expander to see:
- Complete Python strategy implementation
- Class definition with `generate_signals()` method
- Technical indicator calculations
- Entry/exit logic
- First 1000 characters shown (full code available)

### Example Output

After generating "Buy when RSI < 30, sell when RSI > 70":

```
Name: rsi_oversold_strategy
ID: f1db305d-275d-417f-96f1-364578c9a417

┌─────────────┬──────────────┬──────────────┐
│ Sharpe Ratio│ Total Return │ Total Trades │
├─────────────┼──────────────┼──────────────┤
│    1.25     │   +12.3%     │     38       │
└─────────────┴──────────────┴──────────────┘

📄 View Generated Code ▼
```

### What to Expect

**Generation Time:** 3-5 seconds (live LLM inference)

**Code Quality:**
- ✅ Syntactically valid Python
- ✅ Security validated (no dangerous imports)
- ✅ Follows pandas/numpy best practices
- ✅ Ready to execute

**Backtest Data:**
- Uses synthetic price data (for demo)
- Simulates realistic market conditions
- Includes volatility and trends

### Troubleshooting

**"✗ Generation failed"**
- Check your Groq API key in `.env`
- Simplify your strategy description
- Ensure you described both entry AND exit conditions

**Backtest shows 0 trades:**
- Your conditions might be too restrictive
- Try relaxing indicator thresholds
- Example: Change "RSI < 20" to "RSI < 30"

**Low Sharpe ratio:**
- This is normal for some strategies
- Indicates the strategy needs refinement
- Not a bug - it's honest backtesting!

---

## 📝 Feature 3: Contextual RAG Journaling

### What It Does
Captures comprehensive market context when you execute a trade, then generates an AI-powered "trade autopsy" explaining what actually happened vs what you expected.

### How to Use

#### Step 1: Select Feature
Click **"📝 RAG Journaling"** in the sidebar.

#### Step 2: Enter Simulated Trade

**Left Panel - "Simulated Trade":**

1. **Symbol** (text input)
   - Stock ticker you traded
   - Example: `TSLA`

2. **Entry Price** (number input)
   - Price when you bought
   - Example: `250.00`

3. **Exit Price** (number input)
   - Price when you sold
   - Example: `260.00` (profit) or `245.00` (loss)

4. **Quantity** (number input)
   - Number of shares
   - Example: `50`

5. Click **📊 Generate Autopsy**

#### Step 3: Wait for Analysis

**What Happens:**
1. Spinner: "🔍 Capturing market context and generating autopsy..."
2. System fetches:
   - Current market price
   - Technical indicators (RSI, MACD)
   - News headlines (if News API configured)
   - Sentiment analysis
   - Market regime detection
3. LLM generates detailed autopsy report (2-3 seconds)
4. Success: "✅ Autopsy generated!"

#### Step 4: Review Results

**Right Panel - "Trade Autopsy":**

**Market Context (JSON):**
```json
{
  "Symbol": "TSLA",
  "Current Price": "$255.00",
  "RSI": "45.23",
  "News Articles": 5,
  "Sentiment": "0.65"
}
```

**Reads as:**
- **Current Price:** Real-time market price
- **RSI:** Relative Strength Index (0-100)
  - < 30: Oversold
  - 30-70: Normal
  - \> 70: Overbought
- **News Articles:** Number of recent headlines captured
- **Sentiment:** -1.0 (very negative) to +1.0 (very positive)

**Full Autopsy Report (Expandable):**
Click **"📋 Full Autopsy Report"** to expand.

**Report Sections:**

1. **WHAT HAPPENED:**
   - Chronological breakdown of the trade
   - Entry conditions at the time
   - Market movements during holding period
   - Exit conditions when closed

2. **INTENT vs REALITY:**
   - What you thought would happen
   - What actually happened
   - Gap analysis

3. **MARKET CONTEXT:**
   - News events during trade period
   - Sentiment shifts
   - Sector performance
   - Broader market conditions

4. **TECHNICAL ANALYSIS:**
   - Indicator states at entry/exit
   - Signal confirmations/contradictions
   - Pattern recognition

5. **LESSONS LEARNED:**
   - What went right
   - What went wrong
   - Specific improvements for next time
   - Pattern recognition for future trades

### Example Scenarios

#### Winning Trade Example
```
Symbol: TSLA
Entry: $250.00
Exit: $260.00
Quantity: 50
P&L: +$500 (+4%)
```

**Autopsy Highlights:**
- "Entry coincided with positive earnings surprise"
- "RSI was 35 (oversold) - good timing"
- "News sentiment shifted from 0.3 to 0.7 during hold"
- "Lesson: Earnings plays near support levels worked well"

#### Losing Trade Example
```
Symbol: TSLA
Entry: $250.00
Exit: $245.00
Quantity: 50
P&L: -$250 (-2%)
```

**Autopsy Highlights:**
- "Entry during high-volatility regime"
- "Negative news broke 2 hours after entry"
- "RSI was 68 (near overbought) - poor timing"
- "Lesson: Avoid entries when RSI > 65 in volatile markets"

### Understanding the Value

**Traditional Journaling:**
- Manual notes (time-consuming)
- Missing market context
- Subjective interpretation
- No sentiment/news correlation

**RAG Journaling:**
- ✅ Automatic context capture
- ✅ Objective data (price, indicators, news)
- ✅ AI-powered analysis
- ✅ Actionable lessons

### What to Expect

**Context Capture:** 1-2 seconds
- Fetches real-time data
- Calculates technical indicators
- Retrieves news (if API configured)

**Autopsy Generation:** 2-3 seconds
- LLM analyzes all captured data
- Generates 2000-3000 character report
- Structured format with clear sections

**News API Notes:**
- If you see "News Articles: 0", your News API key might be invalid
- System still works - uses simulated market data
- Sentiment will be `null` without news

---

## 🌐 Feature 4: Retail Intelligence Layer

### What It Does
Deploys 4 specialized AI agents in parallel to gather institutional-grade market intelligence. Like having a Bloomberg terminal for retail traders.

### How to Use

#### Step 1: Select Feature
Click **"🌐 Intelligence Layer"** in the sidebar.

#### Step 2: Enter Symbol
At the top, there's a text input labeled "Symbol to analyze":
- Enter any stock ticker
- Examples: `NVDA`, `AAPL`, `TSLA`, `MSFT`, `GOOGL`

#### Step 3: Gather Intelligence
Click the **🔍 Gather Intelligence** button.

**What Happens Next:**
1. Spinner: "🤖 Deploying 4 specialized agents..."
2. All 4 agents run in parallel (2-3 seconds total):
   - **NewsAgent:** Fetches latest headlines
   - **SentimentAgent:** Analyzes social/news sentiment
   - **TechnicalAgent:** Calculates RSI, MACD, volume ratios
   - **VolatilityAgent:** Determines market regime
3. LLM synthesizes all intelligence into actionable insights
4. Success: "✅ Intelligence gathered in X.XXs"

#### Step 4: Review Intelligence

**Agent Status Section:**
4 columns showing agent badges:
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│✓NewsAgent│ │✓Sentiment│ │✓Technical│ │✓Volatilty│
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

All should show **green "✓ Active"** status.

**Intelligence Synthesis Metrics:**
Three key metrics displayed:

1. **Risk Score: X/10**
   - 0-3: Low risk (bullish environment)
   - 4-6: Moderate risk (neutral/mixed signals)
   - 7-10: High risk (bearish/volatile conditions)

2. **Confidence: X%**
   - How confident the AI is in its assessment
   - 0-50%: Low confidence (conflicting signals)
   - 50-75%: Moderate confidence
   - 75-100%: High confidence (strong consensus)

3. **Agents: X/4**
   - Number of agents that successfully responded
   - 4/4: All agents active ✅
   - 3/4: One agent failed ⚠️
   - <3/4: Multiple failures ❌

**Key Signals:**
Bullet list of the 3 most important signals detected:
- "MACD bullish crossover detected"
- "High volume indicates strong momentum"
- "RSI approaching overbought (68)"

Each signal is actionable and time-sensitive.

**Institutional Edge (Blue Info Box):**
Shows what professional/institutional traders know that retail traders typically miss:

Examples:
- "💡 Options flow shows heavy call buying at $900 strike"
- "💡 Large block trades detected at $850 support level"
- "💡 Institutional ownership increased 5% last quarter"

This is the **information asymmetry reducer** - leveling the playing field.

**Recommended Actions:**
Specific, actionable steps based on the intelligence:
- "Consider taking profits on existing positions"
- "Wait for pullback to $875 support before entering"
- "Watch for resistance at $895"
- "Set stop loss at $840"

### Example: Analyzing NVDA

```
Symbol: NVDA
```

**Possible Output:**

```
Intelligence Synthesis:
┌──────────┬──────────┬──────────┐
│Risk: 7/10│Conf: 85% │Agents:4/4│
└──────────┴──────────┴──────────┘

Key Signals:
• MACD bullish crossover detected
• High volume (2.5x average) indicates institutional buying
• RSI at 68 - approaching overbought territory

💡 Institutional Edge:
Options market shows significant $900 call activity expiring next week,
suggesting smart money expects upside breakout.

Recommended Actions:
• Consider scaling into position if price pulls back to $875
• Watch for resistance at $895 - may face profit-taking
• Set trailing stop at 3% below entry to protect gains
```

### Understanding Each Agent

#### 1. NewsAgent 📰
**What it does:**
- Fetches latest news headlines from NewsAPI
- Filters for relevance to the symbol
- Validates source credibility

**Output includes:**
- Article titles
- Publication sources
- Timestamps
- URLs

**Note:** Requires News API key. Without it, returns simulated news.

#### 2. SentimentAgent 😊😐😞
**What it does:**
- Analyzes news headlines with LLM
- Assigns sentiment score (-1.0 to +1.0)
- Identifies key themes (bullish/bearish narratives)

**Sentiment Scale:**
- +0.7 to +1.0: Very bullish
- +0.3 to +0.7: Bullish
- -0.3 to +0.3: Neutral
- -0.7 to -0.3: Bearish
- -1.0 to -0.7: Very bearish

#### 3. TechnicalAgent 📊
**What it does:**
- Calculates RSI (Relative Strength Index)
- Computes MACD (Moving Average Convergence Divergence)
- Analyzes volume ratios vs average

**Provides signals like:**
- "RSI oversold (potential buy)"
- "MACD bearish crossover (sell signal)"
- "High volume (strong momentum)"

#### 4. VolatilityAgent 📈📉
**What it does:**
- Calculates historical volatility
- Estimates implied volatility
- Determines market regime

**Market Regimes:**
- **Low Volatility:** Stable, range-bound market
- **Normal:** Typical market conditions
- **High Volatility:** Large price swings, elevated risk

**Risk Levels:**
- Low: Safe for position sizing
- Medium: Use standard risk management
- High: Reduce position sizes, tighten stops

### What to Expect

**Execution Time:** 2-3 seconds for all 4 agents in parallel

**Success Indicators:**
- All 4 agents show ✓ status
- Confidence > 50%
- Synthesis contains specific, actionable recommendations

**Potential Issues:**
- **News API 401 Error:** Invalid or missing News API key (system continues with simulated data)
- **LLM Synthesis Error:** Rare JSON parsing issue (shows fallback synthesis)
- **Slow Response:** >5 seconds usually means network latency

### Real-World Usage

**Before Entering a Trade:**
1. Run intelligence on target symbol
2. Check risk score (avoid entering if >7/10)
3. Review key signals for confirmation
4. Note institutional edge for timing
5. Follow recommended actions

**Portfolio Monitoring:**
1. Run weekly on all holdings
2. Compare risk scores over time
3. Exit if confidence drops below 40%
4. Rebalance based on regime changes

---

## 🎛️ Dashboard Controls & Navigation

### Sidebar Navigation
- Click any feature name to switch views
- Current feature is highlighted
- Navigation is instant (no page reload)

### System Info Panel (Sidebar Bottom)
**Groq API:** 
- ✓ Configured: System ready
- ✗ Missing: Add to `.env` file

**News API:**
- ✓ Configured: Full news integration
- ✗ Optional: Works without it

**Engines:**
- 4/4 Active: All systems operational
- <4: Initialization issues

### Refresh/Reset
- **Refresh Results:** Click the feature button again
- **Clear Form:** Refresh the browser page (F5)
- **Reset State:** Stop dashboard (Ctrl+C) and restart

### Expandable Sections
Look for **▼** arrows to expand/collapse:
- Code previews
- Full autopsy reports  
- Detailed metrics

Click the header to toggle.

---

## ⚙️ Configuration & Settings

### API Keys (.env file)
Located in project root: `zerodha/.env`

```env
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# Optional but recommended
NEWS_API_KEY=your_newsapi_key_here

# Optional (for advanced features)
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=us-east-1-aws
```

**Getting API Keys:**
- **Groq:** https://console.groq.com/ (Free tier available)
- **NewsAPI:** https://newsapi.org/ (Free tier: 100 requests/day)
- **Pinecone:** https://www.pinecone.io/ (Free tier available)

### User Constitution (Advanced)
Located in `dashboard.py` line ~123:

```python
constitution = UserConstitution(
    max_position_size=10000,      # Max $ per position
    max_daily_loss=500,            # Daily loss limit
    blocked_symbols=["GME", "AMC"], # Banned tickers
    trading_hours_only=False       # Trading hours check
)
```

**Customization:**
- Change `max_position_size` to your comfort level
- Add more `blocked_symbols` for discipline
- Set `trading_hours_only=True` for market hours only

**Apply Changes:**
1. Edit `dashboard.py`
2. Stop dashboard (Ctrl+C)
3. Restart: `streamlit run dashboard.py`

---

## 🐛 Troubleshooting

### Dashboard Won't Start

**Error: "No module named 'streamlit'"**
```bash
pip install streamlit
```

**Error: "GROQ_API_KEY not found"**
1. Create `.env` file in project root
2. Add: `GROQ_API_KEY=your_key_here`
3. Restart dashboard

**Port Already in Use:**
```bash
streamlit run dashboard.py --server.port 8502
```
Then go to: http://localhost:8502

### Features Not Working

**"Engines: 0/4 Active"**
- Missing GROQ_API_KEY
- Check terminal for error messages
- Verify `.env` file exists

**"Generation failed" in Strategy Engine**
- Check Groq API key validity
- Try simpler strategy description
- Check terminal logs for details

**Slow Performance (>10 seconds)**
- Normal for first request (cold start)
- Subsequent requests should be faster
- Check internet connection for LLM API

### Visual Issues

**Dashboard Looks Broken:**
- Try a different browser (Chrome recommended)
- Clear browser cache (Ctrl+F5)
- Check terminal for CSS errors

**Mobile Display:**
- Dashboard is optimized for desktop
- Use landscape mode on tablets
- Desktop/laptop recommended for demos

### API Errors

**News API 401:**
- Invalid News API key
- System continues with simulated data
- Optional feature - doesn't break core functionality

**Groq Rate Limit:**
- Free tier has request limits
- Wait 60 seconds and try again
- Consider upgrading to paid tier

---

## 📊 Performance Expectations

### Response Times
- **Sentinel Checks:** <1ms (deterministic), ~500ms (LLM edge cases)
- **Strategy Generation:** 3-5 seconds
- **Journal Autopsy:** 2-3 seconds
- **Intelligence Gathering:** 2-3 seconds (4 agents in parallel)

### Data Freshness
- **Market Data:** Simulated (demo mode)
- **News:** Real-time (if News API configured)
- **LLM Responses:** Live inference (not cached)
- **Technical Indicators:** Calculated on-demand

### Resource Usage
- **Memory:** ~200-300MB
- **CPU:** Moderate during LLM calls
- **Network:** ~1-5MB per feature invocation

---

## 💡 Tips for Best Results

### General
1. **Keep Dashboard Running:** Don't restart between demos
2. **Use Chrome/Edge:** Best compatibility
3. **Stable Internet:** Required for LLM API calls
4. **Desktop Display:** Optimized for large screens

### Pre-Trade Sentinel
- Test extreme cases to showcase power
- Try banned symbols (GME, AMC)
- Use large quantities to trigger size limits

### Strategy Engine
- Be specific with entry/exit conditions
- Mention specific indicators (RSI, MACD, MA)
- Include risk management (stop loss, take profit)

### RAG Journaling
- Use realistic entry/exit prices
- Try both winning and losing trades
- Compare different market conditions

### Intelligence Layer
- Use popular tickers for best results (AAPL, TSLA, NVDA)
- Run multiple times to see consistency
- Compare similar stocks (tech vs energy, etc.)

---

## 🎓 Advanced Usage

### Comparing Strategies
1. Generate strategy A
2. Note the Sharpe ratio and returns
3. Scroll up and enter different description
4. Generate strategy B
5. Compare metrics side-by-side (use screenshots)

### Building a Trading Journal
1. Use RAG Journaling for every trade
2. Copy autopsy reports to a document
3. Review weekly to identify patterns
4. Refine strategies based on lessons

### Market Sentiment Dashboard
1. Run Intelligence Layer on portfolio holdings daily
2. Track risk scores over time
3. Create watchlist of high-confidence opportunities
4. Monitor regime changes for allocation shifts

---

## 🚀 Ready to Present!

You now know how to use every feature in the dashboard. For presenting to judges, see **[DEMO_GUIDE.md](DEMO_GUIDE.md)** for a polished 5-minute script.

**Quick Demo Checklist:**
- ✅ Dashboard running on http://localhost:8501
- ✅ Groq API key configured
- ✅ All 4 features tested and working
- ✅ Browser window maximized for visibility
- ✅ Internet connection stable

**Have fun showing off the AI agents!** 🤖✨
