# Quick Start Guide

## Installation

### 1. Clone and Setup
```bash
cd d:\comp\zerodha
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Verify Installation
```bash
python -c "import src; print('✅ Installation successful!')"
```

## Running Demos

### UI Adaptation Demo (Recommended First!)
```bash
python demos/ui_adaptation_demo.py
```

**What it shows**: Vision-based approach adapts to UI changes while hardcoded scripts break.

**Output**: Screenshots in `screenshots/` directory showing before/after layouts.

---

### Pre-Trade Sentinel Demo
```bash
python demos/sentinel_demo.py
```

**What it shows**: Real-time trade blocking with <50ms latency.

**Output**: Test results showing which trades were approved/blocked and why.

---

### Strategy Generation Demo
```bash
python demos/strategy_generation_demo.py
```

**What it shows**: Natural language → backtested Python strategies.

**Output**: Generated code, backtest results, approval status.

---

## Interactive Mode

Start the full system:
```bash
python src/main.py
```

### Commands

**Execute a trade**:
```
>>> trade: buy 10 AAPL at market
```

**Generate a strategy**:
```
>>> strategy: buy when RSI < 30 and sell when RSI > 70
```

**View insights**:
```
>>> insights
```

**Exit**:
```
>>> exit
```

## Example Workflow

1. **Create a strategy**:
```
>>> strategy: buy on golden cross, sell on death cross
```

2. **Review backtest results** (auto-displayed)

3. **Execute a trade**:
```
>>> trade: buy 50 MSFT
```

4. **Check if sentinel approved** (auto-displayed)

5. **View trade autopsy**:
```
>>> insights
```

## Troubleshooting

### "GROQ_API_KEY not found"
- Make sure `.env` file exists in project root
- Verify `GROQ_API_KEY=gsk_...` is set correctly
- Restart your terminal after editing `.env`

### "Import Error"
```bash
# Make sure you're in the project root
cd d:\comp\zerodha

# Reinstall dependencies
pip install -r requirements.txt
```

### "Perception taking too long"
- Check your internet connection to Groq API
- Reduce screenshot resolution in code
- Switch to faster model (llama-3.1-8b-instant)

### "Sentinel blocking all trades"
- Check user constitution settings in `.env`
- Increase `MAX_POSITION_SIZE` and `MAX_DAILY_LOSS`
- Set `ENABLE_KILL_SWITCH=false` for testing

## Next Steps

1. **Read the TRD**: [Technical Deep Dive](docs/TECHNICAL_DEEP_DIVE.md)
2. **Customize your constitution**: [Configuration](docs/CONFIGURATION.md)
3. **Integrate with real broker**: See broker API docs
4. **Deploy to production**: [Deployment Guide](docs/DEPLOYMENT.md) (coming soon)

## Getting Help

- **Issues**: Check logs in `logs/` directory
- **Documentation**: See `docs/` folder
- **Examples**: Browse `demos/` folder
- **Code**: All source in `src/` folder

## Safety Reminders

⚠️ **This is experimental software. Trade at your own risk.**

- Always start with **paper trading**
- Test strategies thoroughly before going live
- Keep kill switch enabled (`ENABLE_KILL_SWITCH=true`)
- Monitor logs regularly
- Start with small position sizes

✅ **Best Practices**:
- Run demos first to understand the system
- Create a conservative user constitution
- Backtest strategies for at least 30 days
- Enable all safety features
- Review trade autopsies regularly
