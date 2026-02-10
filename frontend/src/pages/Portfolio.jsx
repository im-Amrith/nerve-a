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
  PieChart,
  DollarSign,
  BarChart3,
  RefreshCw,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  Briefcase,
  Target,
  AlertTriangle,
  Plus,
  Minus,
  PlayCircle,
  Settings
} from 'lucide-react'
import axios from 'axios'
import './Portfolio.css'

const API_BASE = 'http://localhost:8003/api'

// Sidebar Navigation
function Sidebar({ activeTab, setActiveTab }) {
  const navigate = useNavigate()
  
  const tabs = [
    { id: 'overview', icon: Activity, label: 'Overview', route: '/markets' },
    { id: 'portfolio', icon: Briefcase, label: 'Portfolio', route: '/portfolio' },
    { id: 'sentinel', icon: Shield, label: 'Sentinel', route: '/dashboard' },
    { id: 'strategy', icon: Brain, label: 'Strategy', route: '/dashboard' },
    { id: 'journal', icon: BookOpen, label: 'Journal', route: '/dashboard' },
    { id: 'intelligence', icon: TrendingUp, label: 'Intelligence', route: '/dashboard' },
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

// Mock portfolio data
const mockHoldings = [
  { symbol: 'NVDA', name: 'NVIDIA Corporation', quantity: 50, avgCost: 875, currentPrice: 920, change: 5.14, sector: 'Technology' },
  { symbol: 'AAPL', name: 'Apple Inc.', quantity: 100, avgCost: 175, currentPrice: 182, change: 4.0, sector: 'Technology' },
  { symbol: 'TSLA', name: 'Tesla Inc.', quantity: 30, avgCost: 240, currentPrice: 225, change: -6.25, sector: 'Automotive' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', quantity: 25, avgCost: 140, currentPrice: 155, change: 10.71, sector: 'Technology' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', quantity: 40, avgCost: 178, currentPrice: 185, change: 3.93, sector: 'Consumer' },
  { symbol: 'META', name: 'Meta Platforms', quantity: 35, avgCost: 485, currentPrice: 520, change: 7.22, sector: 'Technology' },
  { symbol: 'MSFT', name: 'Microsoft Corp.', quantity: 45, avgCost: 380, currentPrice: 415, change: 9.21, sector: 'Technology' },
  { symbol: 'JPM', name: 'JPMorgan Chase', quantity: 60, avgCost: 185, currentPrice: 195, change: 5.41, sector: 'Financial' },
]

const mockWatchlist = [
  { symbol: 'AMD', name: 'AMD Inc.', price: 165.50, change: 3.2 },
  { symbol: 'CRM', name: 'Salesforce', price: 285.75, change: -1.5 },
  { symbol: 'NFLX', name: 'Netflix', price: 612.30, change: 2.8 },
  { symbol: 'DIS', name: 'Disney', price: 98.45, change: -0.8 },
]

function Portfolio() {
  const navigate = useNavigate()
  const [holdings, setHoldings] = useState(mockHoldings)
  const [watchlist, setWatchlist] = useState(mockWatchlist)
  const [loading, setLoading] = useState(false)

  // Calculate portfolio metrics
  const totalValue = holdings.reduce((sum, h) => sum + (h.currentPrice * h.quantity), 0)
  const totalCost = holdings.reduce((sum, h) => sum + (h.avgCost * h.quantity), 0)
  const totalPL = totalValue - totalCost
  const totalPLPercent = ((totalPL / totalCost) * 100)
  const dayPL = holdings.reduce((sum, h) => sum + (h.currentPrice * h.quantity * h.change / 100), 0)

  // Sector allocation
  const sectorAllocation = holdings.reduce((acc, h) => {
    const value = h.currentPrice * h.quantity
    acc[h.sector] = (acc[h.sector] || 0) + value
    return acc
  }, {})

  const sectorColors = {
    'Technology': '#3b82f6',
    'Automotive': '#ef4444',
    'Consumer': '#22c55e',
    'Financial': '#eab308'
  }

  return (
    <div className="portfolio-page">
      <Sidebar activeTab="portfolio" setActiveTab={() => {}} />
      
      <main className="portfolio-main">
        {/* Portfolio Hero */}
        <div className="portfolio-hero">
          <div className="hero-left">
            <h1 className="portfolio-title">PORTFOLIO</h1>
            <p className="portfolio-subtitle">Real-Time Holdings & Performance Analytics</p>
          </div>
          <div className="hero-right">
            <button className="btn-refresh" onClick={() => setLoading(true)}>
              <RefreshCw size={18} className={loading ? 'spin' : ''} />
              REFRESH
            </button>
          </div>
        </div>

        {/* Portfolio Stats */}
        <div className="portfolio-stats">
          <div className="stat-card total-value">
            <div className="stat-icon">
              <DollarSign size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">TOTAL VALUE</span>
              <span className="stat-value">${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
          
          <div className="stat-card total-pl">
            <div className="stat-icon">
              {totalPL >= 0 ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
            </div>
            <div className="stat-content">
              <span className="stat-label">TOTAL P&L</span>
              <span className={`stat-value ${totalPL >= 0 ? 'positive' : 'negative'}`}>
                {totalPL >= 0 ? '+' : ''}${totalPL.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                <span className="stat-pct">({totalPLPercent >= 0 ? '+' : ''}{totalPLPercent.toFixed(2)}%)</span>
              </span>
            </div>
          </div>
          
          <div className="stat-card day-pl">
            <div className="stat-icon">
              <Activity size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">TODAY'S P&L</span>
              <span className={`stat-value ${dayPL >= 0 ? 'positive' : 'negative'}`}>
                {dayPL >= 0 ? '+' : ''}${dayPL.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
          
          <div className="stat-card positions">
            <div className="stat-icon">
              <Briefcase size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">POSITIONS</span>
              <span className="stat-value">{holdings.length}</span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="portfolio-grid">
          {/* Holdings Table */}
          <div className="holdings-section">
            <div className="section-header">
              <h2>Holdings</h2>
              <button className="btn-add">
                <Plus size={16} />
                Add Position
              </button>
            </div>
            
            <div className="holdings-table">
              <div className="table-header">
                <span>Symbol</span>
                <span>Qty</span>
                <span>Avg Cost</span>
                <span>Current</span>
                <span>Market Value</span>
                <span>P&L</span>
                <span>Change</span>
              </div>
              
              {holdings.map((holding, i) => {
                const marketValue = holding.currentPrice * holding.quantity
                const pl = (holding.currentPrice - holding.avgCost) * holding.quantity
                const plPercent = ((holding.currentPrice - holding.avgCost) / holding.avgCost) * 100
                
                return (
                  <motion.div
                    key={holding.symbol}
                    className="table-row"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <div className="symbol-cell">
                      <span className="symbol">{holding.symbol}</span>
                      <span className="name">{holding.name}</span>
                    </div>
                    <span className="qty">{holding.quantity}</span>
                    <span className="avg-cost">${holding.avgCost.toFixed(2)}</span>
                    <span className="current">${holding.currentPrice.toFixed(2)}</span>
                    <span className="market-value">${marketValue.toLocaleString()}</span>
                    <span className={`pl ${pl >= 0 ? 'positive' : 'negative'}`}>
                      {pl >= 0 ? '+' : ''}${pl.toFixed(2)}
                    </span>
                    <span className={`change ${holding.change >= 0 ? 'positive' : 'negative'}`}>
                      {holding.change >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                      {Math.abs(holding.change).toFixed(2)}%
                    </span>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="portfolio-sidebar">
            {/* Sector Allocation */}
            <div className="allocation-card">
              <h3>Sector Allocation</h3>
              <div className="allocation-chart">
                {Object.entries(sectorAllocation).map(([sector, value]) => {
                  const percentage = (value / totalValue) * 100
                  return (
                    <div key={sector} className="allocation-item">
                      <div className="allocation-label">
                        <span className="sector-dot" style={{ background: sectorColors[sector] }} />
                        <span>{sector}</span>
                      </div>
                      <div className="allocation-bar-container">
                        <div 
                          className="allocation-bar" 
                          style={{ width: `${percentage}%`, background: sectorColors[sector] }}
                        />
                      </div>
                      <span className="allocation-pct">{percentage.toFixed(1)}%</span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Watchlist */}
            <div className="watchlist-card">
              <div className="watchlist-header">
                <h3>Watchlist</h3>
                <button className="btn-add-small">
                  <Plus size={14} />
                </button>
              </div>
              <div className="watchlist-items">
                {watchlist.map((item) => (
                  <div key={item.symbol} className="watchlist-item">
                    <div className="watchlist-info">
                      <span className="watchlist-symbol">{item.symbol}</span>
                      <span className="watchlist-name">{item.name}</span>
                    </div>
                    <div className="watchlist-price">
                      <span className="price">${item.price.toFixed(2)}</span>
                      <span className={`change ${item.change >= 0 ? 'positive' : 'negative'}`}>
                        {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Metrics */}
            <div className="risk-card">
              <h3>Risk Metrics</h3>
              <div className="risk-items">
                <div className="risk-item">
                  <span className="risk-label">Portfolio Beta</span>
                  <span className="risk-value">1.24</span>
                </div>
                <div className="risk-item">
                  <span className="risk-label">Sharpe Ratio</span>
                  <span className="risk-value">1.85</span>
                </div>
                <div className="risk-item">
                  <span className="risk-label">Max Drawdown</span>
                  <span className="risk-value negative">-12.4%</span>
                </div>
                <div className="risk-item">
                  <span className="risk-label">Volatility</span>
                  <span className="risk-value">18.5%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Portfolio
