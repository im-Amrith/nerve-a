import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Zap,
  Activity,
  Shield,
  Brain,
  BookOpen,
  TrendingUp,
  TrendingDown,
  Home,
  Briefcase,
  PlayCircle,
  Search,
  Calendar,
  DollarSign,
  BarChart3,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  Clock,
  Percent,
  LineChart,
  AlertTriangle,
  CheckCircle,
  Info,
  Settings
} from 'lucide-react'
import axios from 'axios'
import './Simulation.css'

const API_BASE = 'http://localhost:8003/api'

// Sidebar Navigation
function Sidebar({ activeTab, setActiveTab }) {
  const navigate = useNavigate()
  
  const tabs = [
    { id: 'overview', icon: Activity, label: 'Overview', route: '/markets' },
    { id: 'sentinel', icon: Shield, label: 'Sentinel', route: '/dashboard' },
    { id: 'strategy', icon: Brain, label: 'Strategy', route: '/dashboard' },
    { id: 'journal', icon: BookOpen, label: 'Journal', route: '/dashboard' },
    { id: 'intelligence', icon: TrendingUp, label: 'Intelligence', route: '/dashboard' },
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
            className={`nav-item ${tab.id === 'simulation' ? 'active' : ''}`}
            onClick={() => navigate(tab.route)}
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

// Mock historical data generator
function generateHistoricalData(symbol, startDate, endDate, startPrice) {
  const data = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  let price = startPrice
  let currentDate = new Date(start)
  
  while (currentDate <= end) {
    // Skip weekends
    if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
      const volatility = 0.02
      const drift = 0.0003
      const change = (Math.random() - 0.5) * 2 * volatility + drift
      price = price * (1 + change)
      
      data.push({
        date: currentDate.toISOString().split('T')[0],
        price: parseFloat(price.toFixed(2)),
        volume: Math.floor(Math.random() * 10000000) + 1000000
      })
    }
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  return data
}

// Popular stocks for quick selection
const popularStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 178.50 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 141.25 },
  { symbol: 'MSFT', name: 'Microsoft Corp.', price: 378.90 },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 485.75 },
  { symbol: 'TSLA', name: 'Tesla Inc.', price: 248.30 },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 178.15 },
  { symbol: 'META', name: 'Meta Platforms', price: 505.60 },
  { symbol: 'JPM', name: 'JPMorgan Chase', price: 195.40 },
]

function Simulation() {
  const navigate = useNavigate()
  const [symbol, setSymbol] = useState('')
  const [quantity, setQuantity] = useState(100)
  const [entryDate, setEntryDate] = useState('2025-01-02')
  const [exitDate, setExitDate] = useState('2026-02-10')
  const [entryPrice, setEntryPrice] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [simulationResult, setSimulationResult] = useState(null)
  const [selectedStock, setSelectedStock] = useState(null)
  const [searchResults, setSearchResults] = useState([])

  // Handle stock search
  const handleSearch = (query) => {
    setSymbol(query.toUpperCase())
    if (query.length > 0) {
      const filtered = popularStocks.filter(
        s => s.symbol.includes(query.toUpperCase()) || 
             s.name.toLowerCase().includes(query.toLowerCase())
      )
      setSearchResults(filtered)
    } else {
      setSearchResults([])
    }
  }

  // Select a stock
  const selectStock = (stock) => {
    setSymbol(stock.symbol)
    setSelectedStock(stock)
    setEntryPrice(stock.price.toString())
    setSearchResults([])
  }

  // Run simulation
  const runSimulation = async () => {
    if (!symbol || !quantity || !entryDate || !exitDate) {
      return
    }

    setIsLoading(true)

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500))

    const stock = selectedStock || popularStocks.find(s => s.symbol === symbol) || {
      symbol: symbol,
      name: symbol,
      price: parseFloat(entryPrice) || 100
    }

    const startPrice = parseFloat(entryPrice) || stock.price
    const historicalData = generateHistoricalData(symbol, entryDate, exitDate, startPrice)
    
    if (historicalData.length === 0) {
      setIsLoading(false)
      return
    }

    const finalPrice = historicalData[historicalData.length - 1].price
    const initialInvestment = startPrice * quantity
    const currentValue = finalPrice * quantity
    const absolutePL = currentValue - initialInvestment
    const percentagePL = ((finalPrice - startPrice) / startPrice) * 100

    // Calculate additional metrics
    const prices = historicalData.map(d => d.price)
    const maxPrice = Math.max(...prices)
    const minPrice = Math.min(...prices)
    const maxDrawdown = ((maxPrice - minPrice) / maxPrice) * 100
    
    // Calculate daily returns for volatility
    const returns = []
    for (let i = 1; i < prices.length; i++) {
      returns.push((prices[i] - prices[i-1]) / prices[i-1])
    }
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
    const volatility = Math.sqrt(
      returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
    ) * Math.sqrt(252) * 100

    // Find best and worst days
    let bestDay = { date: '', change: -Infinity }
    let worstDay = { date: '', change: Infinity }
    for (let i = 1; i < historicalData.length; i++) {
      const change = ((historicalData[i].price - historicalData[i-1].price) / historicalData[i-1].price) * 100
      if (change > bestDay.change) {
        bestDay = { date: historicalData[i].date, change }
      }
      if (change < worstDay.change) {
        worstDay = { date: historicalData[i].date, change }
      }
    }

    setSimulationResult({
      stock,
      historicalData,
      metrics: {
        initialInvestment,
        currentValue,
        absolutePL,
        percentagePL,
        startPrice,
        finalPrice,
        maxPrice,
        minPrice,
        maxDrawdown,
        volatility,
        tradingDays: historicalData.length,
        bestDay,
        worstDay
      }
    })

    setIsLoading(false)
  }

  // Reset simulation
  const resetSimulation = () => {
    setSimulationResult(null)
    setSymbol('')
    setSelectedStock(null)
    setEntryPrice('')
    setQuantity(100)
  }

  return (
    <div className="simulation-page">
      <Sidebar />
      
      <main className="simulation-main">
        {/* Hero Header */}
        <div className="simulation-hero">
          <div className="simulation-hero-content">
            <h1 className="simulation-title">TRADE SIMULATOR</h1>
            <p className="simulation-subtitle">Backtest your trades and analyze historical market behavior</p>
          </div>
          {simulationResult && (
            <button className="btn-reset" onClick={resetSimulation}>
              <RefreshCw size={18} />
              New Simulation
            </button>
          )}
        </div>

        {!simulationResult ? (
          /* Input Form */
          <motion.div 
            className="simulation-form-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="form-section">
              <h2><Search size={20} /> Select Stock</h2>
              
              <div className="stock-search">
                <div className="search-input-wrapper">
                  <Search className="search-icon" size={18} />
                  <input
                    type="text"
                    placeholder="Search by symbol or name..."
                    value={symbol}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="stock-input"
                  />
                </div>
                
                {searchResults.length > 0 && (
                  <div className="search-dropdown">
                    {searchResults.map(stock => (
                      <div 
                        key={stock.symbol}
                        className="search-result"
                        onClick={() => selectStock(stock)}
                      >
                        <span className="result-symbol">{stock.symbol}</span>
                        <span className="result-name">{stock.name}</span>
                        <span className="result-price">${stock.price.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="quick-select">
                <span className="quick-label">Quick Select:</span>
                <div className="quick-chips">
                  {popularStocks.slice(0, 6).map(stock => (
                    <button
                      key={stock.symbol}
                      className={`stock-chip ${selectedStock?.symbol === stock.symbol ? 'active' : ''}`}
                      onClick={() => selectStock(stock)}
                    >
                      {stock.symbol}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label><DollarSign size={16} /> Entry Price</label>
                <input
                  type="number"
                  placeholder="0.00"
                  value={entryPrice}
                  onChange={(e) => setEntryPrice(e.target.value)}
                  step="0.01"
                />
              </div>

              <div className="form-group">
                <label><BarChart3 size={16} /> Quantity</label>
                <input
                  type="number"
                  placeholder="100"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
                />
              </div>

              <div className="form-group">
                <label><Calendar size={16} /> Entry Date</label>
                <input
                  type="date"
                  value={entryDate}
                  onChange={(e) => setEntryDate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label><Calendar size={16} /> Exit Date</label>
                <input
                  type="date"
                  value={exitDate}
                  onChange={(e) => setExitDate(e.target.value)}
                />
              </div>
            </div>

            <div className="investment-summary">
              <div className="summary-item">
                <span className="summary-label">Total Investment</span>
                <span className="summary-value">
                  ${((parseFloat(entryPrice) || 0) * quantity).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Shares</span>
                <span className="summary-value">{quantity.toLocaleString()}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Period</span>
                <span className="summary-value">
                  {entryDate && exitDate ? 
                    Math.ceil((new Date(exitDate) - new Date(entryDate)) / (1000 * 60 * 60 * 24)) + ' days' : 
                    '--'}
                </span>
              </div>
            </div>

            <button 
              className="btn-simulate"
              onClick={runSimulation}
              disabled={!symbol || !quantity || !entryPrice || isLoading}
            >
              {isLoading ? (
                <>
                  <RefreshCw className="spin" size={20} />
                  Running Simulation...
                </>
              ) : (
                <>
                  <PlayCircle size={20} />
                  Run Simulation
                </>
              )}
            </button>
          </motion.div>
        ) : (
          /* Results */
          <motion.div 
            className="simulation-results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {/* Stock Info Header */}
            <div className="result-header">
              <div className="stock-info">
                <h2>{simulationResult.stock.symbol}</h2>
                <span className="stock-name">{simulationResult.stock.name}</span>
              </div>
              <div className={`result-badge ${simulationResult.metrics.percentagePL >= 0 ? 'positive' : 'negative'}`}>
                {simulationResult.metrics.percentagePL >= 0 ? <ArrowUpRight size={20} /> : <ArrowDownRight size={20} />}
                {simulationResult.metrics.percentagePL >= 0 ? '+' : ''}{simulationResult.metrics.percentagePL.toFixed(2)}%
              </div>
            </div>

            {/* Key Metrics */}
            <div className="metrics-grid">
              <div className="metric-card primary">
                <div className="metric-icon">
                  <DollarSign size={24} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">INITIAL INVESTMENT</span>
                  <span className="metric-value">${simulationResult.metrics.initialInvestment.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon final">
                  <Target size={24} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">FINAL VALUE</span>
                  <span className="metric-value">${simulationResult.metrics.currentValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                </div>
              </div>

              <div className={`metric-card ${simulationResult.metrics.absolutePL >= 0 ? 'profit' : 'loss'}`}>
                <div className={`metric-icon ${simulationResult.metrics.absolutePL >= 0 ? 'profit' : 'loss'}`}>
                  {simulationResult.metrics.absolutePL >= 0 ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                </div>
                <div className="metric-content">
                  <span className="metric-label">PROFIT / LOSS</span>
                  <span className={`metric-value ${simulationResult.metrics.absolutePL >= 0 ? 'positive' : 'negative'}`}>
                    {simulationResult.metrics.absolutePL >= 0 ? '+' : ''}${simulationResult.metrics.absolutePL.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon days">
                  <Clock size={24} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">TRADING DAYS</span>
                  <span className="metric-value">{simulationResult.metrics.tradingDays}</span>
                </div>
              </div>
            </div>

            {/* Price Chart */}
            <div className="chart-section">
              <h3><LineChart size={18} /> Price History</h3>
              <div className="price-chart">
                <div className="chart-container">
                  {/* Simple SVG line chart */}
                  <svg viewBox="0 0 800 300" className="chart-svg">
                    {/* Grid lines */}
                    {[0, 1, 2, 3, 4].map(i => (
                      <line 
                        key={i}
                        x1="50" 
                        y1={50 + i * 50} 
                        x2="780" 
                        y2={50 + i * 50} 
                        stroke="rgba(255,255,255,0.05)" 
                        strokeWidth="1"
                      />
                    ))}
                    
                    {/* Price line */}
                    <path
                      d={(() => {
                        const data = simulationResult.historicalData
                        const minP = simulationResult.metrics.minPrice * 0.98
                        const maxP = simulationResult.metrics.maxPrice * 1.02
                        const range = maxP - minP
                        
                        return data.map((d, i) => {
                          const x = 50 + (i / (data.length - 1)) * 730
                          const y = 250 - ((d.price - minP) / range) * 200
                          return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                        }).join(' ')
                      })()}
                      fill="none"
                      stroke={simulationResult.metrics.percentagePL >= 0 ? '#22c55e' : '#ef4444'}
                      strokeWidth="2"
                    />
                    
                    {/* Entry point */}
                    <circle
                      cx="50"
                      cy={250 - ((simulationResult.historicalData[0].price - simulationResult.metrics.minPrice * 0.98) / ((simulationResult.metrics.maxPrice * 1.02) - (simulationResult.metrics.minPrice * 0.98))) * 200}
                      r="6"
                      fill="#3b82f6"
                    />
                    
                    {/* Exit point */}
                    <circle
                      cx="780"
                      cy={250 - ((simulationResult.historicalData[simulationResult.historicalData.length - 1].price - simulationResult.metrics.minPrice * 0.98) / ((simulationResult.metrics.maxPrice * 1.02) - (simulationResult.metrics.minPrice * 0.98))) * 200}
                      r="6"
                      fill={simulationResult.metrics.percentagePL >= 0 ? '#22c55e' : '#ef4444'}
                    />
                  </svg>
                  
                  {/* Price labels */}
                  <div className="chart-labels">
                    <div className="price-label max">${simulationResult.metrics.maxPrice.toFixed(2)}</div>
                    <div className="price-label mid">${((simulationResult.metrics.maxPrice + simulationResult.metrics.minPrice) / 2).toFixed(2)}</div>
                    <div className="price-label min">${simulationResult.metrics.minPrice.toFixed(2)}</div>
                  </div>
                </div>
                
                <div className="chart-legend">
                  <span className="legend-item">
                    <span className="dot entry"></span>
                    Entry: ${simulationResult.metrics.startPrice.toFixed(2)}
                  </span>
                  <span className="legend-item">
                    <span className={`dot exit ${simulationResult.metrics.percentagePL >= 0 ? 'positive' : 'negative'}`}></span>
                    Exit: ${simulationResult.metrics.finalPrice.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            {/* Analysis Cards */}
            <div className="analysis-grid">
              <div className="analysis-card">
                <h4><BarChart3 size={16} /> Price Range</h4>
                <div className="analysis-items">
                  <div className="analysis-row">
                    <span>Highest Price</span>
                    <span className="value positive">${simulationResult.metrics.maxPrice.toFixed(2)}</span>
                  </div>
                  <div className="analysis-row">
                    <span>Lowest Price</span>
                    <span className="value negative">${simulationResult.metrics.minPrice.toFixed(2)}</span>
                  </div>
                  <div className="analysis-row">
                    <span>Price Range</span>
                    <span className="value">${(simulationResult.metrics.maxPrice - simulationResult.metrics.minPrice).toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="analysis-card">
                <h4><Percent size={16} /> Risk Metrics</h4>
                <div className="analysis-items">
                  <div className="analysis-row">
                    <span>Max Drawdown</span>
                    <span className="value negative">-{simulationResult.metrics.maxDrawdown.toFixed(2)}%</span>
                  </div>
                  <div className="analysis-row">
                    <span>Volatility (Ann.)</span>
                    <span className="value">{simulationResult.metrics.volatility.toFixed(2)}%</span>
                  </div>
                  <div className="analysis-row">
                    <span>CAGR</span>
                    <span className={`value ${simulationResult.metrics.percentagePL >= 0 ? 'positive' : 'negative'}`}>
                      {simulationResult.metrics.percentagePL >= 0 ? '+' : ''}{(simulationResult.metrics.percentagePL * (365 / simulationResult.metrics.tradingDays)).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="analysis-card">
                <h4><Activity size={16} /> Notable Days</h4>
                <div className="analysis-items">
                  <div className="analysis-row">
                    <span>Best Day</span>
                    <span className="value positive">+{simulationResult.metrics.bestDay.change.toFixed(2)}%</span>
                  </div>
                  <div className="analysis-row">
                    <span>Worst Day</span>
                    <span className="value negative">{simulationResult.metrics.worstDay.change.toFixed(2)}%</span>
                  </div>
                  <div className="analysis-row">
                    <span>Avg Daily Move</span>
                    <span className="value">{(simulationResult.metrics.volatility / Math.sqrt(252)).toFixed(3)}%</span>
                  </div>
                </div>
              </div>

              <div className="analysis-card insight">
                <h4><Info size={16} /> AI Insight</h4>
                <p className="insight-text">
                  {simulationResult.metrics.percentagePL >= 0 ? (
                    simulationResult.metrics.percentagePL > 20 ? 
                      `Excellent performance! Your ${simulationResult.stock.symbol} position gained ${simulationResult.metrics.percentagePL.toFixed(1)}% with a max drawdown of ${simulationResult.metrics.maxDrawdown.toFixed(1)}%. The risk-adjusted return looks favorable.` :
                      `Solid returns on ${simulationResult.stock.symbol}. Consider the ${simulationResult.metrics.volatility.toFixed(1)}% annualized volatility when sizing future positions.`
                  ) : (
                    simulationResult.metrics.percentagePL > -10 ?
                      `Minor loss on ${simulationResult.stock.symbol}. With ${simulationResult.metrics.volatility.toFixed(1)}% volatility, this is within normal range. Consider averaging down if fundamentals remain strong.` :
                      `Significant drawdown detected. Review your entry timing and consider setting stop-losses at the ${simulationResult.metrics.minPrice.toFixed(2)} support level.`
                  )}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  )
}

export default Simulation
