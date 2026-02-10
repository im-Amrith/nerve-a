# Agentic Brokerage OS

An intelligence-first brokerage layer that governs trading through autonomous AI agents.

## 🎯 Core Philosophy
**Problem**: Brittle execution-only models lead to retail losses through emotional trading and lack of behavioral guardrails.

**Solution**: Self-healing adaptive automation using Vision Language Models and multi-agent orchestration.

## � **Interactive Dashboard (Recommended for Judges)**

We've built a beautiful web-based dashboard to showcase all features interactively!

### One-Click Launch (Windows):
```bash
run_dashboard.bat
```

### One-Click Launch (Linux/Mac):
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Manual Launch:
```bash
# Install Streamlit
pip install streamlit>=1.30.0

# Launch dashboard
streamlit run dashboard.py
```

**Then open your browser to:** http://localhost:8501

The dashboard provides:
- ✅ Interactive demos of all 4 core features
- ✅ Real-time visualization of AI agents
- ✅ Live code generation and execution
- ✅ Beautiful UI for judges to evaluate
- ✅ One-click feature switching

## �🏗️ Architecture

```
Perception (CV + Groq VLM) → Reasoning (LangGraph) → Action (Trading APIs)
```

### Core Components
- **Orchestrator**: LangGraph-based multi-agent coordination
- **Perception Engine**: Computer Vision + Groq for UI understanding (no DOM selectors)
- **Reasoning Engine**: LLM-based planning and decision-making
- **Pre-Trade Sentinel**: Sub-50ms safety checks and kill switch
- **Strategy Engine**: Natural language to executable trading algorithms
- **RAG Journaling**: Context-aware trade autopsy system

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=your_environment
```

### Run the System
```bash
# Start the orchestrator
python src/main.py

# Run demos
python demos/ui_adaptation_demo.py
python demos/strategy_generation_demo.py
```

## 📁 Project Structure

```
zerodha/
├── src/
│   ├── agents/              # Specialized agents
│   │   ├── perception_agent.py
│   │   ├── reasoning_agent.py
│   │   ├── sentinel_agent.py
│   │   └── strategy_agent.py
│   ├── core/                # Core systems
│   │   ├── orchestrator.py  # LangGraph workflow
│   │   ├── perception.py    # CV + VLM perception
│   │   └── state.py         # Agent state definitions
│   ├── engines/             # Business logic
│   │   ├── pre_trade_sentinel.py
│   │   ├── strategy_engine.py
│   │   └── rag_journal.py
│   ├── utils/               # Utilities
│   │   ├── vision.py
│   │   ├── memory.py
│   │   └── validators.py
│   └── main.py              # Entry point
├── demos/                   # Demonstrations
├── tests/                   # Test suite
├── config/                  # Configuration files
└── docs/                    # Documentation
```

## 🎪 Demos

### 1. UI Adaptation Demo ("Sabotage Test")
Demonstrates self-healing when UI elements are moved/modified.
```bash
python demos/ui_adaptation_demo.py
```

### 2. Strategy Generation
Convert natural language to backtested trading algorithms.
```bash
python demos/strategy_generation_demo.py
```

### 3. Pre-Trade Sentinel
Live demonstration of the kill switch blocking risky trades.
```bash
python demos/sentinel_demo.py
```

## 🔐 Security Features
- **Zero-Knowledge ML**: Verifiable inference without data exposure
- **User Constitution**: Personalized trading rules and guardrails
- **Kill Switch**: Hard blocks on rule violations (<50ms latency)

## 📊 Key Metrics
- **Perception Latency**: <200ms for screen-to-JSON mapping
- **Sentinel Response**: <50ms for trade safety checks
- **UI Adaptation**: Real-time self-healing without code changes

## 🛠️ Technology Stack
- **VLM**: Groq (llama-3.2-90b-vision-preview)
- **Agent Framework**: LangGraph
- **Vector DB**: Pinecone
- **Computer Vision**: OpenCV + Pillow
- **API Layer**: FastAPI (future)

## 📝 License
MIT

## 🤝 Contributing
See [CONTRIBUTING.md](docs/CONTRIBUTING.md)
