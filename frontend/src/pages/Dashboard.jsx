import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Shield,
  Brain,
  BookOpen,
  TrendingUp,
  Home,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Zap,
  Activity,
  BarChart3,
  Newspaper,
  MessageSquare,
  ChevronRight,
  Save,
  Trash2,
  Play,
  Terminal,
  Settings,
  Briefcase,
  PlayCircle
} from 'lucide-react'
import axios from 'axios'
import './Dashboard.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003/api'

// Sidebar Navigation
function Sidebar({ activeTab, setActiveTab }) {
  const navigate = useNavigate()
  
  const tabs = [
    { id: 'overview', icon: Activity, label: 'Overview', route: '/markets' },
    { id: 'sentinel', icon: Shield, label: 'Sentinel' },
    { id: 'strategy', icon: Brain, label: 'Strategy' },
    { id: 'journal', icon: BookOpen, label: 'Journal' },
    { id: 'intelligence', icon: TrendingUp, label: 'Intelligence' },
    { id: 'portfolio', icon: Briefcase, label: 'Portfolio', route: '/portfolio' },
    { id: 'simulation', icon: PlayCircle, label: 'Simulation', route: '/simulation' },
    { id: 'settings', icon: Settings, label: 'Settings', route: '/settings' },
  ]

  return (
    <div className="sidebar">
      <div className="sidebar-header" onClick={() => navigate('/markets')}>
        <Zap className="logo-icon nerve-icon" />
        <span>NERVE</span>
      </div>
      
      <nav className="sidebar-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => tab.route ? navigate(tab.route) : setActiveTab(tab.id)}
          >
            <tab.icon size={20} />
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="nav-item" onClick={() => navigate('/')}>
          <Home size={20} />
          <span>Landing</span>
        </button>
      </div>
    </div>
  )
}

// Sentinel Panel
function SentinelPanel() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [form, setForm] = useState({
    symbol: 'TSLA',
    action: 'buy',
    quantity: 100,
    price: 250
  })
  
  // Mock real-time data
  const [marketData, setMarketData] = useState({
    price: 190,
    change: 2.9,
    dailyPL: 1050,
    lossLimit: -5000
  })

  const checkTrade = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/sentinel/check`, form)
      setResult(res.data)
    } catch (error) {
      setResult({ error: error.message })
    }
    setLoading(false)
  }

  return (
    <div className="panel">
      {/* Sentinel Hero Header */}
      <div className="sentinel-hero">
        <h1 className="sentinel-title">PRE-TRADE SENTINEL</h1>
        <p className="sentinel-subtitle">Live market data integration active. Validating against risk constitution.</p>
        <div className="sentinel-stats">
          <span className="stat-item">
            DAILY P/L: <span className="stat-value positive">${marketData.dailyPL.toLocaleString()}</span>
          </span>
          <span className="stat-divider">/</span>
          <span className="stat-item">
            LOSS LIMIT: <span className="stat-value negative">${marketData.lossLimit.toLocaleString()}</span>
          </span>
        </div>
        <div className="sentinel-price-bar">
          <div className="price-info">
            <span className="price-label">REAL-TIME PRICE</span>
            <span className="price-value">${marketData.price}</span>
          </div>
          <div className="price-info">
            <span className="price-label">24H CHANGE</span>
            <span className={`change-value ${marketData.change >= 0 ? 'positive' : 'negative'}`}>
              {marketData.change >= 0 ? '+' : ''}{marketData.change}%
            </span>
          </div>
        </div>
      </div>

      <div className="panel-header">
        <Shield className="panel-icon" />
        <div>
          <h2>Trade Validation</h2>
          <p>Real-time safety checks with &lt;50ms latency</p>
        </div>
      </div>

      <div className="panel-content">
        <div className="form-grid">
          <div className="form-group">
            <label>Symbol</label>
            <input
              type="text"
              value={form.symbol}
              onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })}
              placeholder="TSLA"
            />
          </div>
          <div className="form-group">
            <label>Action</label>
            <select value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })}>
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              value={form.quantity}
              onChange={(e) => setForm({ ...form, quantity: parseInt(e.target.value) })}
            />
          </div>
          <div className="form-group">
            <label>Price ($)</label>
            <input
              type="number"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: parseFloat(e.target.value) })}
            />
          </div>
        </div>

        <button className="btn-action" onClick={checkTrade} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={20} /> : <Shield size={20} />}
          {loading ? 'Checking...' : 'Check Trade'}
        </button>

        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              className={`result-card ${result.approved ? 'approved' : 'blocked'}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="result-header">
                {result.approved ? (
                  <CheckCircle className="result-icon success" size={28} />
                ) : (
                  <XCircle className="result-icon danger" size={28} />
                )}
                <div>
                  <h3>{result.approved ? 'APPROVED' : 'BLOCKED'}</h3>
                  {result.latency_ms && <span>{result.latency_ms}ms latency</span>}
                </div>
              </div>

              <div className="result-body">
                <div className="risk-meter">
                  <span>Risk Score</span>
                  <div className="meter-bar">
                    <div 
                      className="meter-fill"
                      style={{ 
                        width: `${(result.risk_score || 0) * 100}%`,
                        background: result.risk_score > 0.7 ? '#ff4757' : result.risk_score > 0.4 ? '#ffa502' : '#2ed573'
                      }}
                    />
                  </div>
                  <span>{((result.risk_score || 0) * 100).toFixed(0)}%</span>
                </div>

                <p className="reasoning">{result.reasoning}</p>

                {result.violated_rules?.length > 0 && (
                  <div className="violations">
                    <h4>Violated Rules:</h4>
                    <ul>
                      {result.violated_rules.map((rule, i) => (
                        <li key={i}><AlertTriangle size={14} /> {rule}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Strategy Panel
function StrategyPanel() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [description, setDescription] = useState('')
  const [symbol, setSymbol] = useState('SPY')

  const placeholderText = `Describe your strategy in plain English...
Example: Create a mean reversion strategy on SPY using RSI(14). Buy when RSI < 30 and price is above the 200 SMA. Sell when RSI > 70.`

  const generateStrategy = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post(`${API_BASE}/strategy/generate`, {
        strategy_description: description,
        backtest_symbol: symbol
      })
      setResult(res.data)
    } catch (error) {
      setResult({ error: error.message })
    }
    setLoading(false)
  }

  return (
    <div className="panel strategy-panel">
      {/* Strategy Header */}
      <div className="strategy-header">
        <div className="strategy-title-section">
          <h1 className="strategy-title">STRATEGY ENGINE</h1>
          <p className="strategy-subtitle">Natural Language to Python Strategy Compiler</p>
        </div>
        <div className="strategy-actions">
          <button className="btn-save">
            <Save size={16} />
            SAVE
          </button>
          <button className="btn-delete">
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="strategy-workspace">
        {/* Left: Input Panel */}
        <div className="strategy-input-panel">
          <textarea
            className="strategy-textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={placeholderText}
          />
          <button className="btn-generate" onClick={generateStrategy} disabled={loading}>
            {loading ? <RefreshCw className="spin" size={18} /> : <Settings size={18} />}
            {loading ? 'GENERATING...' : 'GENERATE STRATEGY CODE'}
          </button>
        </div>

        {/* Right: Code Output Panel */}
        <div className="strategy-output-panel">
          <div className="code-panel-header">
            <Terminal size={14} />
            <span>strategy.py</span>
          </div>
          <div className="code-panel-body">
            {result?.strategy_code ? (
              <pre className="strategy-code">{result.strategy_code}</pre>
            ) : (
              <div className="code-placeholder">// WAITING FOR INPUT...</div>
            )}
          </div>
          <div className="code-panel-footer">
            <button className="btn-backtest" disabled={!result?.strategy_code}>
              <Play size={14} />
              BACKTEST NOW
            </button>
            <button className="btn-paper-trade" disabled={!result?.strategy_code}>
              PAPER TRADE
            </button>
          </div>
        </div>
      </div>

      {/* Backtest Results */}
      <AnimatePresence mode="wait">
        {result?.backtest_results && (
          <motion.div
            className="backtest-results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="backtest-metrics">
              <div className="metric">
                <span className="metric-label">Total Return</span>
                <span className={`metric-value ${result.backtest_results.total_return >= 0 ? 'positive' : 'negative'}`}>
                  {(result.backtest_results.total_return * 100).toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Sharpe Ratio</span>
                <span className="metric-value">{result.backtest_results.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Max Drawdown</span>
                <span className="metric-value negative">
                  {(result.backtest_results.max_drawdown * 100).toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Trades</span>
                <span className="metric-value">{result.backtest_results.total_trades}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Win Rate</span>
                <span className="metric-value">{(result.backtest_results.win_rate * 100).toFixed(1)}%</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {result?.error && (
        <div className="error-message">
          <XCircle size={20} />
          <span>{result.error}</span>
        </div>
      )}
    </div>
  )
}

// Journal Panel
function JournalPanel() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [form, setForm] = useState({
    symbol: 'NVDA',
    action: 'buy',
    quantity: 50,
    entry_price: 875,
    exit_price: 920,
    rationale: 'Bought on AI chip demand thesis before earnings'
  })

  const generateAutopsy = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post(`${API_BASE}/journal/autopsy`, form)
      setResult(res.data)
    } catch (error) {
      setResult({ error: error.message })
    }
    setLoading(false)
  }

  return (
    <div className="panel journal-panel">
      {/* Journal Header */}
      <div className="journal-hero">
        <div className="journal-title-section">
          <h1 className="journal-title">RAG JOURNALING</h1>
          <p className="journal-subtitle">AI-Powered Trade Autopsy with Semantic Search</p>
        </div>
        <button className="btn-gather" onClick={generateAutopsy} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={18} /> : <BookOpen size={18} />}
          {loading ? 'ANALYZING...' : 'GENERATE AUTOPSY'}
        </button>
      </div>

      {/* Trade Form */}
      <div className="journal-form-section">
        <div className="journal-form-grid">
          <div className="journal-form-group">
            <label>SYMBOL</label>
            <input
              type="text"
              value={form.symbol}
              onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })}
            />
          </div>
          <div className="journal-form-group">
            <label>ACTION</label>
            <select value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })}>
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          <div className="journal-form-group">
            <label>QUANTITY</label>
            <input
              type="number"
              value={form.quantity}
              onChange={(e) => setForm({ ...form, quantity: parseInt(e.target.value) })}
            />
          </div>
          <div className="journal-form-group">
            <label>ENTRY PRICE ($)</label>
            <input
              type="number"
              value={form.entry_price}
              onChange={(e) => setForm({ ...form, entry_price: parseFloat(e.target.value) })}
            />
          </div>
          <div className="journal-form-group">
            <label>EXIT PRICE ($)</label>
            <input
              type="number"
              value={form.exit_price}
              onChange={(e) => setForm({ ...form, exit_price: parseFloat(e.target.value) })}
            />
          </div>
        </div>

        <div className="journal-form-group full">
          <label>TRADE RATIONALE</label>
          <textarea
            value={form.rationale}
            onChange={(e) => setForm({ ...form, rationale: e.target.value })}
            rows={3}
            placeholder="Why did you make this trade? What was your thesis?"
          />
        </div>
      </div>

      {/* Autopsy Results */}
      <AnimatePresence mode="wait">
        {result && result.autopsy && (
          <motion.div
            className="autopsy-results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="autopsy-header">
              <h3>Trade Autopsy Report</h3>
              <div className="autopsy-pnl">
                <span className={result.autopsy.pnl >= 0 ? 'positive' : 'negative'}>
                  {result.autopsy.pnl >= 0 ? '+' : ''}${result.autopsy.pnl?.toFixed(2)}
                </span>
                <span className="pnl-pct">({result.autopsy.pnl_pct?.toFixed(2)}%)</span>
              </div>
            </div>

            <div className="autopsy-cards">
              <div className="autopsy-card">
                <div className="autopsy-card-header">
                  <Activity size={16} />
                  <h4>Market Context</h4>
                </div>
                {typeof result.autopsy.market_context === 'object' ? (
                  <div className="market-context-details">
                    {result.autopsy.market_context.summary && <p><strong>Summary:</strong> {result.autopsy.market_context.summary}</p>}
                    {result.autopsy.market_context.market_sentiment && <p><strong>Sentiment:</strong> {result.autopsy.market_context.market_sentiment}</p>}
                    {result.autopsy.market_context.industry_trend && <p><strong>Industry:</strong> {result.autopsy.market_context.industry_trend}</p>}
                    {result.autopsy.market_context.macroeconomic_factors && <p><strong>Macro:</strong> {result.autopsy.market_context.macroeconomic_factors}</p>}
                  </div>
                ) : (
                  <p>{result.autopsy.market_context}</p>
                )}
              </div>

              <div className="autopsy-card">
                <div className="autopsy-card-header">
                  <Brain size={16} />
                  <h4>Analysis</h4>
                </div>
                <p>{typeof result.autopsy.analysis === 'object'
                  ? JSON.stringify(result.autopsy.analysis)
                  : result.autopsy.analysis}</p>
              </div>

              {result.autopsy.lessons_learned && result.autopsy.lessons_learned.length > 0 && (
                <div className="autopsy-card lessons">
                  <div className="autopsy-card-header">
                    <BookOpen size={16} />
                    <h4>Lessons Learned</h4>
                  </div>
                  <ul>
                    {result.autopsy.lessons_learned.map((lesson, i) => (
                      <li key={i}><ChevronRight size={14} /> {lesson}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {result?.error && (
          <div className="error-message">
            <XCircle size={20} />
            <span>{result.error}</span>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Intelligence Panel
function IntelligencePanel() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [query, setQuery] = useState('')
  const [lastScan, setLastScan] = useState(null)

  const gatherIntelligence = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post(`${API_BASE}/intelligence/gather`, { symbol: query || 'market sentiment' })
      setResult(res.data.intelligence)
      setLastScan(new Date().toLocaleTimeString())
    } catch (error) {
      setResult({ error: error.message })
    }
    setLoading(false)
  }

  // Extract news articles from raw intelligence
  const getNewsArticles = () => {
    if (!result) return []
    const articles = []
    
    // Get headlines from NewsAgent
    const newsAgent = result.raw_intelligence?.find(i => i.source === 'NewsAgent')
    if (newsAgent?.headlines) {
      newsAgent.headlines.forEach(h => {
        if (h && typeof h === 'object' && h.title) {
          articles.push({
            category: h.category || 'MARKET NEWS',
            title: h.title,
            summary: h.summary || '',
            source: h.source || 'News',
            url: h.url || '#',
            sentiment: h.sentiment || 'neutral'
          })
        }
      })
    }

    // Get sentiment analysis as an article
    const sentimentAgent = result.raw_intelligence?.find(i => i.source === 'SentimentAgent')
    if (sentimentAgent) {
      articles.push({
        category: 'SENTIMENT ANALYST',
        title: `${result.symbol || query} Sentiment Analysis`,
        summary: sentimentAgent.key_themes?.join('. ') || `Current sentiment is ${sentimentAgent.overall_sentiment || 'neutral'}`,
        source: 'AI Analysis',
        url: '#',
        sentiment: sentimentAgent.overall_sentiment?.toLowerCase() || 'neutral'
      })
    }

    // Add technical analysis as article
    const technicalAgent = result.raw_intelligence?.find(i => i.source === 'TechnicalAgent')
    if (technicalAgent) {
      const rsi = technicalAgent.rsi
      const macd = technicalAgent.macd
      const trend = technicalAgent.trend
      articles.push({
        category: 'TECHNICAL ANALYSIS',
        title: `RSI ${rsi ? (rsi > 70 ? 'Overbought' : rsi < 30 ? 'Oversold' : 'Neutral') : 'N/A'} at ${rsi?.toFixed(1) || 'N/A'}`,
        summary: `MACD: ${macd?.toFixed(3) || 'N/A'}, Current trend is ${trend || 'neutral'}. ${rsi > 70 ? 'Consider taking profits.' : rsi < 30 ? 'Potential buying opportunity.' : 'Wait for clearer signals.'}`,
        source: 'Technical Indicators',
        url: '#',
        sentiment: trend === 'bullish' ? 'bullish' : trend === 'bearish' ? 'bearish' : 'neutral'
      })
    }

    // Add volatility analysis as article
    const volatilityAgent = result.raw_intelligence?.find(i => i.source === 'VolatilityAgent')
    if (volatilityAgent) {
      const vol = volatilityAgent.historical_vol
      const beta = volatilityAgent.beta
      const risk = volatilityAgent.risk
      articles.push({
        category: 'VOLATILITY REPORT',
        title: `${risk === 'high' ? 'High' : risk === 'low' ? 'Low' : 'Moderate'} Risk Profile - Beta ${beta?.toFixed(2) || 'N/A'}`,
        summary: `Historical volatility: ${vol ? (vol * 100).toFixed(1) + '%' : 'N/A'}. ${beta > 1.2 ? 'Stock moves more than the market.' : beta < 0.8 ? 'Stock is less volatile than market.' : 'Stock moves with the market.'}`,
        source: 'Risk Analytics',
        url: '#',
        sentiment: risk === 'high' ? 'bearish' : risk === 'low' ? 'bullish' : 'neutral'
      })
    }

    // Add synthesis insights as articles
    if (result.synthesis?.key_signals) {
      result.synthesis.key_signals.forEach((signal, i) => {
        if (typeof signal === 'string' && signal.length > 10) {
          articles.push({
            category: 'AI INTELLIGENCE',
            title: signal.length > 80 ? signal.substring(0, 80) + '...' : signal,
            summary: result.synthesis.summary || '',
            source: 'NERVE AI',
            url: '#',
            sentiment: result.synthesis.risk_score > 6 ? 'bearish' : result.synthesis.risk_score < 4 ? 'bullish' : 'neutral'
          })
        }
      })
    }

    // Add recommended actions as articles
    if (result.synthesis?.recommended_actions) {
      result.synthesis.recommended_actions.forEach((action, i) => {
        if (typeof action === 'string' && action.length > 10 && i < 2) {
          articles.push({
            category: 'RECOMMENDED ACTION',
            title: action.length > 80 ? action.substring(0, 80) + '...' : action,
            summary: `Risk Score: ${result.synthesis.risk_score}/10 | Confidence: ${result.synthesis.confidence}%`,
            source: 'NERVE AI',
            url: '#',
            sentiment: result.synthesis.risk_score > 6 ? 'bearish' : result.synthesis.risk_score < 4 ? 'bullish' : 'neutral'
          })
        }
      })
    }

    return articles.slice(0, 9)
  }

  const articles = result ? getNewsArticles() : []

  return (
    <div className="panel intel-panel">
      {/* Intelligence Header */}
      <div className="intel-hero">
        <div className="intel-title-section">
          <h1 className="intel-title">RETAIL INTELLIGENCE LAYER</h1>
          {lastScan && <span className="last-scan">LAST SCAN: {lastScan}</span>}
        </div>
        <button className="btn-gather" onClick={gatherIntelligence} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={18} /> : <Settings size={18} />}
          {loading ? 'GATHERING...' : 'GATHER INTELLIGENCE'}
        </button>
      </div>

      {/* Search Bar */}
      <div className="intel-search-bar">
        <div className="search-input-wrapper">
          <input
            type="text"
            className="intel-search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search topic, symbol, or market sentiment..."
            onKeyDown={(e) => e.key === 'Enter' && gatherIntelligence()}
          />
        </div>
        <div className="search-badges">
          <span className="search-badge">SEARCH ENABLED</span>
          <span className="search-badge active">LIVE</span>
        </div>
      </div>

      {/* Results */}
      <AnimatePresence mode="wait">
        {result && !result.error && articles.length > 0 && (
          <motion.div
            className="intel-articles-grid"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {articles.map((article, i) => (
              <motion.div
                key={i}
                className="intel-article-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="article-header">
                  <span className="article-category">{article.category}</span>
                  <span className={`article-sentiment ${article.sentiment}`}>
                    {article.sentiment.toUpperCase()}
                  </span>
                </div>
                <h3 className="article-title">{article.title}</h3>
                {article.summary && (
                  <p className="article-summary">{article.summary.substring(0, 150)}{article.summary.length > 150 ? '...' : ''}</p>
                )}
                <div className="article-source">
                  <Zap size={12} />
                  <span>SOURCE: {article.source.toUpperCase()}</span>
                </div>
                <div className="article-actions">
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="btn-read">
                    READ <ChevronRight size={14} />
                  </a>
                  <button className="btn-watch">
                    <Activity size={14} /> WATCH
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {result && !result.error && articles.length === 0 && (
          <div className="intel-empty">
            <p>No articles found. Try a different search query.</p>
          </div>
        )}

        {result?.error && (
          <div className="error-message">
            <XCircle size={20} />
            <span>{result.error}</span>
          </div>
        )}
      </AnimatePresence>

      {!result && !loading && (
        <div className="intel-empty">
          <Newspaper size={48} />
          <p>Enter a topic or symbol and click "Gather Intelligence" to get AI-powered market insights.</p>
        </div>
      )}
    </div>
  )
}

// Main Dashboard Component
function Dashboard() {
  const [activeTab, setActiveTab] = useState('sentinel')

  const renderPanel = () => {
    switch (activeTab) {
      case 'sentinel':
        return <SentinelPanel />
      case 'strategy':
        return <StrategyPanel />
      case 'journal':
        return <JournalPanel />
      case 'intelligence':
        return <IntelligencePanel />
      default:
        return <SentinelPanel />
    }
  }

  return (
    <div className="dashboard">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="dashboard-main">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {renderPanel()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default Dashboard
