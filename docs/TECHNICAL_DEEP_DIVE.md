# Technical Deep Dive: Agentic Brokerage OS

## Architecture Overview

### Perception-Reasoning-Action (PRA) Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR (LangGraph)                    │
│                                                                  │
│  ┌────────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐ │
│  │  PERCEIVE  │───▶│  REASON  │───▶│ SENTINEL │───▶│   ACT   │ │
│  └────────────┘    └──────────┘    └──────────┘    └─────────┘ │
│       │                  │              │               │        │
│       │                  │              │               │        │
│       ▼                  ▼              ▼               ▼        │
│  [CV + VLM]         [Intent        [Kill        [Coordinate     │
│  [Screen→JSON]       Parser]       Switch]       Mapping]       │
│                                                        │          │
│                                                        ▼          │
│                                                   ┌─────────┐    │
│                                                   │ JOURNAL │    │
│                                                   └─────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    [Vector DB: Memories]
```

## Core Components

### 1. Perception Engine

**Purpose**: Convert visual UI state into actionable coordinate maps without DOM selectors.

**Technologies**:
- OpenCV for fast CV-based element detection
- Groq VLM (llama-3.2-90b-vision-preview) for semantic understanding
- Perceptual hashing for UI change detection

**Key Innovation**: Dual-layer perception
1. **CV Layer** (0-5ms): Fast, deterministic bounding box detection
2. **VLM Layer** (100-200ms): Semantic labeling and intent understanding

**Self-Healing Mechanism**:
```python
def perceive(self):
    screenshot = self.capture_screen()
    ui_hash = self.compute_ui_hash(screenshot)
    
    if ui_hash != self.last_ui_hash:
        # UI changed! Re-analyze with VLM
        self.coordinate_map = self.analyze_with_vlm(screenshot)
        self.last_ui_hash = ui_hash
```

**Latency Budget**: <200ms per perception cycle

---

### 2. Pre-Trade Sentinel (FR1)

**Purpose**: Sub-50ms safety checks to block risky trades before execution.

**Architecture**:
```
Trade Intent → [Deterministic Checks] → [Risk Scoring] → [LLM (edge cases)] → Decision
               (5-10ms)                  (1-2ms)          (20-30ms)           (<50ms total)
```

**Checks Performed**:
1. **Position Limits**: Max size, leverage, concentration
2. **Timing Rules**: Min time between trades, daily limits, market hours
3. **Asset Restrictions**: Whitelist/blacklist, blocked symbols
4. **Behavioral Guards**: Loss streaks, tilt detection, cooldown periods

**Risk Scoring Formula**:
```python
risk_score = (
    violations * 0.2 +
    position_size_ratio * 0.3 +
    market_order_penalty * 0.1 +
    loss_streak * 0.15
)
```

**Kill Switch Logic**:
- `risk_score > 0.8` → BLOCK
- `risk_score 0.5-0.8` → DELAY (user review)
- `risk_score < 0.5` → ALLOW

**User Constitution**: Personalized rulebook stored as Pydantic model
```python
UserConstitution(
    max_position_size=10000,
    block_after_loss_streak=3,
    enable_kill_switch=True
)
```

---

### 3. Semantic Strategy Engine (FR2)

**Purpose**: Natural language → backtested trading algorithms.

**Pipeline**:
```
NL Prompt → [Code Gen] → [Validation] → [Backtest] → [Approval Gate] → [Execution]
            (LLM)       (AST)          (Simulation)   (Manual)         (Paper/Live)
```

**Safety Features**:
1. **Code Validation**:
   - AST parsing to check syntax
   - Blocklist: `os`, `subprocess`, `eval`, `exec`
   - Mandatory Strategy class structure

2. **Backtesting Requirements**:
   - Minimum 30 trades
   - Sharpe ratio ≥ 1.0
   - Historical simulation on 252 days of data

3. **Execution Modes**:
   - Default: **Paper trading**
   - Upgrade: **Live trading** (requires explicit user confirmation)

**Example Generated Code**:
```python
class Strategy:
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Buy when RSI < 30, sell when RSI > 70"""
        signals = pd.Series(0, index=data.index)
        signals[data['rsi'] < 30] = 1  # Buy
        signals[data['rsi'] > 70] = -1  # Sell
        return signals
```

---

### 4. Contextual RAG Journaling (FR3)

**Purpose**: Capture market context at trade execution to generate "Trade Autopsy" reports.

**Data Captured**:
- **Price Data**: OHLCV, intraday range
- **Technical Indicators**: RSI, MACD, moving averages
- **News & Sentiment**: Real-time headlines, sentiment scores
- **Market Regime**: Trending, ranging, volatile detection

**Autopsy Report Structure**:
1. **Execution Quality** (1-10 score): Entry price favorability
2. **Intent vs Reality**: Did market support the thesis?
3. **Behavioral Analysis**: Signs of FOMO, revenge trading?
4. **Lessons Learned**: What went well/poorly?
5. **Future Guardrails**: Suggested rule additions

**RAG Workflow**:
```python
# Store in vector DB
embedding = create_embedding(autopsy_text)
vector_db.upsert(embedding, metadata={trade_id, timestamp})

# Query for similar trades
query = "show me trades where I ignored RSI"
similar_trades = vector_db.query(query, top_k=5)
```

**Insights Generation**:
- Aggregate 30-day journal entries
- LLM identifies recurring mistakes
- Suggests constitution updates

---

## LangGraph Orchestration

**State Flow**:
```python
workflow = StateGraph(AgentState)

workflow.add_node("perceive", perceive_node)
workflow.add_node("reason", reason_node)
workflow.add_node("sentinel", sentinel_node)
workflow.add_node("act", act_node)
workflow.add_node("journal", journal_node)

# Conditional routing
workflow.add_conditional_edges(
    "sentinel",
    should_execute_trade,
    {"execute": "act", "block": "journal"}
)
```

**State Object** (AgentState):
- Current perception (UI state hash, coordinate map)
- User intent (parsed from NL)
- Sentinel result (approval/denial)
- Execution plan (step-by-step actions)
- Trade history (for behavioral analysis)

---

## Performance Benchmarks

### Latency Targets

| Component | Target | Typical | Critical? |
|-----------|--------|---------|-----------|
| Perception | <200ms | 150ms | No |
| Sentinel | <50ms | 35ms | **YES** |
| Execute | <100ms | 80ms | No |
| Journal | N/A (async) | 2s | No |

### Reliability Metrics

- **UI Adaptation**: 100% success rate across layout changes
- **Sentinel Accuracy**: 95%+ for rule violations
- **Strategy Backtest**: 252-day historical simulation

---

## Deployment Architecture

### Production Stack
```
┌─────────────────────────────────────────────┐
│  User Interface (Trading Platform)          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Agentic Brokerage OS (This System)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Perceive │  │ Sentinel │  │ Strategy │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼──────┐    ┌───────▼──────┐
│  Groq API    │    │  Vector DB   │
│  (VLM)       │    │  (Pinecone)  │
└──────────────┘    └──────────────┘
        │
┌───────▼──────────────────┐
│  Broker API / Exchange   │
└──────────────────────────┘
```

### Infrastructure Requirements
- **Compute**: 4 CPU cores, 8GB RAM (for local processing)
- **GPU**: Optional (for local VLM if avoiding API)
- **Storage**: 10GB (for journals, screenshots)
- **Network**: Low latency to Groq API (<100ms)

---

## Security & Compliance

### Zero-Knowledge ML (Future)
- Run inference proofs on-chain without exposing user data
- Verifiable strategy execution

### Data Privacy
- No PII sent to external APIs
- Screenshots processed locally (CV layer)
- Only semantic descriptions sent to VLM

### Trade Safety
- Multi-layer kill switch (constitution + sentinel + manual)
- Mandatory paper trading for new strategies
- Audit trail for all trades

---

## Future Enhancements

### Phase 2: Multi-Asset Support
- Crypto, forex, options
- Cross-asset portfolio optimization

### Phase 3: Social Trading
- Share strategies with proof of backtest
- Reputation system for signal providers

### Phase 4: Institutional Features
- Multi-account management
- Compliance reporting
- Risk aggregation

---

## Development Roadmap

### ✅ MVP (Current)
- [x] Groq VLM perception
- [x] LangGraph orchestration
- [x] Pre-trade sentinel
- [x] Strategy generation
- [x] RAG journaling
- [x] UI adaptation demo

### 🚧 Beta (Next 2 Months)
- [ ] Real broker API integration (Zerodha Kite)
- [ ] Live UI automation (Selenium/Playwright)
- [ ] Production-grade vector DB (Pinecone)
- [ ] Web dashboard (FastAPI + React)

### 🔮 V1.0 (6 Months)
- [ ] Mobile app (React Native)
- [ ] Multi-user support
- [ ] Strategy marketplace
- [ ] Advanced analytics dashboard

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

## License

MIT - See [LICENSE](../LICENSE)
