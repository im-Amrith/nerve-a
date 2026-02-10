import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  BarChart3,
  Globe,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Newspaper,
  PieChart,
  DollarSign,
  Percent,
  ChevronRight,
  RefreshCw,
  Bell,
  Settings,
  Search,
  Star,
  Eye,
  X,
  Home,
  Shield,
  Brain,
  BookOpen,
  LineChart as LineChartIcon
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import './MarketOverview.css'

// Sidebar Navigation Component
function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const navItems = [
    { id: 'markets', path: '/markets', icon: LineChartIcon, label: 'Markets' },
    { id: 'sentinel', path: '/dashboard', icon: Shield, label: 'Sentinel', state: { tab: 'sentinel' } },
    { id: 'strategy', path: '/dashboard', icon: Brain, label: 'Strategy', state: { tab: 'strategy' } },
    { id: 'journal', path: '/dashboard', icon: BookOpen, label: 'Journal', state: { tab: 'journal' } },
    { id: 'intelligence', path: '/dashboard', icon: TrendingUp, label: 'Intel', state: { tab: 'intelligence' } },
  ]
  
  return (
    <aside className="markets-sidebar">
      <div className="sidebar-brand" onClick={() => navigate('/')}>
        <Zap className="sidebar-brand-icon" />
        <span>NERVE</span>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-nav-item ${location.pathname === item.path && item.id === 'markets' ? 'active' : ''}`}
            onClick={() => navigate(item.path, { state: item.state })}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="sidebar-bottom">
        <button className="sidebar-nav-item" onClick={() => navigate('/')}>
          <Home size={20} />
          <span>Home</span>
        </button>
      </div>
    </aside>
  )
}

// Generate historical price data
const generateHistoricalData = (basePrice, days = 30, volatility = 0.025) => {
  const data = []
  let price = basePrice * 0.92
  
  for (let i = days; i >= 0; i--) {
    const trend = (days - i) / days * 0.1 // Slight upward trend
    const noise = (Math.random() - 0.5) * volatility * price * 2
    const wave = Math.sin(i * 0.3) * price * 0.015
    price = price * (1 + trend * 0.003) + noise + wave
    price = Math.max(price, basePrice * 0.7)
    data.push({
      date: `Day ${days - i + 1}`,
      price: parseFloat(price.toFixed(2)),
      volume: Math.floor(Math.random() * 50 + 20)
    })
  }
  return data
}

// Generate intraday data with realistic variation
const generateIntradayData = (basePrice, points = 96) => {
  const data = []
  let price = basePrice * 0.985
  
  for (let i = 0; i < points; i++) {
    const trend = i / points * 0.02
    const noise = (Math.random() - 0.48) * price * 0.008
    const wave = Math.sin(i * 0.15) * price * 0.005
    price = price * (1 + trend * 0.001) + noise + wave
    price = Math.max(price, basePrice * 0.9)
    data.push({
      time: `${Math.floor(9 + i / 12)}:${String((i % 12) * 5).padStart(2, '0')}`,
      price: parseFloat(price.toFixed(2))
    })
  }
  return data
}

// Simulated market data - in production, this would come from an API
const generatePrice = (base, volatility = 0.02) => {
  const change = (Math.random() - 0.5) * 2 * volatility * base
  return base + change
}

const initialStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 198.45, change: 2.34, changePercent: 1.19, volume: '52.3M', high: 199.62, low: 196.80, historicalData: generateHistoricalData(198.45), intradayData: generateIntradayData(198.45) },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 875.42, change: 18.75, changePercent: 2.19, volume: '41.2M', high: 882.50, low: 858.20, historicalData: generateHistoricalData(875.42), intradayData: generateIntradayData(875.42) },
  { symbol: 'TSLA', name: 'Tesla Inc.', price: 417.89, change: -5.23, changePercent: -1.24, volume: '98.7M', high: 425.40, low: 412.15, historicalData: generateHistoricalData(417.89), intradayData: generateIntradayData(417.89) },
  { symbol: 'MSFT', name: 'Microsoft Corp.', price: 425.12, change: 3.87, changePercent: 0.92, volume: '23.1M', high: 427.80, low: 421.50, historicalData: generateHistoricalData(425.12), intradayData: generateIntradayData(425.12) },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 175.67, change: -1.23, changePercent: -0.70, volume: '28.4M', high: 177.90, low: 174.20, historicalData: generateHistoricalData(175.67), intradayData: generateIntradayData(175.67) },
  { symbol: 'AMZN', name: 'Amazon.com', price: 225.34, change: 4.56, changePercent: 2.06, volume: '45.6M', high: 227.10, low: 220.85, historicalData: generateHistoricalData(225.34), intradayData: generateIntradayData(225.34) },
  { symbol: 'META', name: 'Meta Platforms', price: 612.78, change: 8.92, changePercent: 1.48, volume: '18.9M', high: 618.40, low: 605.30, historicalData: generateHistoricalData(612.78), intradayData: generateIntradayData(612.78) },
  { symbol: 'AMD', name: 'AMD Inc.', price: 178.45, change: -2.18, changePercent: -1.21, volume: '62.3M', high: 182.10, low: 176.90, historicalData: generateHistoricalData(178.45), intradayData: generateIntradayData(178.45) },
]

const indices = [
  { symbol: 'SPY', name: 'S&P 500', price: 5234.18, change: 28.45, changePercent: 0.55 },
  { symbol: 'QQQ', name: 'NASDAQ 100', price: 18456.72, change: 156.34, changePercent: 0.85 },
  { symbol: 'DIA', name: 'DOW JONES', price: 42876.54, change: -89.23, changePercent: -0.21 },
  { symbol: 'IWM', name: 'Russell 2000', price: 2234.67, change: 12.45, changePercent: 0.56 },
]

const marketNews = [
  { id: 1, title: 'Fed signals potential rate cuts in Q2 as inflation cools', source: 'Reuters', time: '2m ago', sentiment: 'bullish' },
  { id: 2, title: 'NVIDIA announces next-gen AI chips, stock surges', source: 'Bloomberg', time: '15m ago', sentiment: 'bullish' },
  { id: 3, title: 'Tech sector leads market rally amid strong earnings', source: 'CNBC', time: '32m ago', sentiment: 'bullish' },
  { id: 4, title: 'Oil prices drop on increased supply concerns', source: 'WSJ', time: '1h ago', sentiment: 'bearish' },
  { id: 5, title: 'Apple Vision Pro sales exceed analyst expectations', source: 'TechCrunch', time: '2h ago', sentiment: 'bullish' },
]

const sectorPerformance = [
  { name: 'Technology', change: 2.34, color: '#60b8ff' },
  { name: 'Healthcare', change: 0.87, color: '#4ade80' },
  { name: 'Financials', change: -0.45, color: '#f87171' },
  { name: 'Energy', change: -1.23, color: '#f87171' },
  { name: 'Consumer', change: 1.56, color: '#4ade80' },
  { name: 'Real Estate', change: 0.23, color: '#4ade80' },
]

// Stock Card Component
function StockCard({ stock, index, onSelect, isSelected }) {
  const isPositive = stock.change >= 0
  const sparklineData = stock.intradayData?.slice(-24) || []
  
  // Calculate domain for sparkline
  const prices = sparklineData.map(d => d.price)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const padding = (maxPrice - minPrice) * 0.1 || maxPrice * 0.01
  
  return (
    <motion.div
      className={`stock-card ${isSelected ? 'selected' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ scale: 1.02, y: -4 }}
      onClick={() => onSelect(stock)}
    >
      <div className="stock-card-header">
        <div className="stock-symbol-wrapper">
          <span className="stock-symbol">{stock.symbol}</span>
          <Star size={14} className="watchlist-star" />
        </div>
        <span className="stock-name">{stock.name}</span>
      </div>
      
      <div className="stock-price-section">
        <span className="stock-price">${stock.price.toFixed(2)}</span>
        <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
          <span>{isPositive ? '+' : ''}{stock.change.toFixed(2)}</span>
          <span className="change-percent">({isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%)</span>
        </div>
      </div>

      <div className="sparkline-container">
        <ResponsiveContainer width="100%" height={50}>
          <AreaChart data={sparklineData} margin={{ top: 5, right: 0, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id={`gradient-${stock.symbol}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={isPositive ? '#4ade80' : '#f87171'} stopOpacity={0.4} />
                <stop offset="100%" stopColor={isPositive ? '#4ade80' : '#f87171'} stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <YAxis domain={[minPrice - padding, maxPrice + padding]} hide />
            <Area
              type="monotone"
              dataKey="price"
              stroke={isPositive ? '#4ade80' : '#f87171'}
              strokeWidth={2}
              fill={`url(#gradient-${stock.symbol})`}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="stock-stats">
        <div className="stat">
          <span className="stat-label">Vol</span>
          <span className="stat-value">{stock.volume}</span>
        </div>
        <div className="stat">
          <span className="stat-label">H</span>
          <span className="stat-value">${stock.high.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">L</span>
          <span className="stat-value">${stock.low.toFixed(2)}</span>
        </div>
      </div>
    </motion.div>
  )
}

// Index Card Component
function IndexCard({ index: indexData, delay }) {
  const isPositive = indexData.change >= 0
  
  return (
    <motion.div
      className={`index-card ${isPositive ? 'positive' : 'negative'}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
    >
      <div className="index-header">
        <span className="index-symbol">{indexData.symbol}</span>
        <span className="index-name">{indexData.name}</span>
      </div>
      <div className="index-price">{indexData.price.toLocaleString()}</div>
      <div className="index-change">
        {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
        <span>{isPositive ? '+' : ''}{indexData.change.toFixed(2)}</span>
        <span>({isPositive ? '+' : ''}{indexData.changePercent.toFixed(2)}%)</span>
      </div>
    </motion.div>
  )
}

// Custom Tooltip Component
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="tooltip-label">{label}</p>
        <p className="tooltip-value">${payload[0].value.toFixed(2)}</p>
      </div>
    )
  }
  return null
}

// Stock Detail Chart Component
function StockDetailChart({ stock, onClose }) {
  const [timeframe, setTimeframe] = useState('1D')
  const isPositive = stock.change >= 0
  
  const chartData = timeframe === '1D' ? stock.intradayData : stock.historicalData
  const dataKey = timeframe === '1D' ? 'time' : 'date'
  
  const minPrice = Math.min(...chartData.map(d => d.price)) * 0.998
  const maxPrice = Math.max(...chartData.map(d => d.price)) * 1.002
  const avgPrice = chartData.reduce((acc, d) => acc + d.price, 0) / chartData.length

  return (
    <motion.div
      className="chart-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="chart-panel-header">
        <div className="chart-stock-info">
          <div className="chart-symbol">{stock.symbol}</div>
          <div className="chart-name">{stock.name}</div>
        </div>
        <div className="chart-price-info">
          <span className="chart-current-price">${stock.price.toFixed(2)}</span>
          <span className={`chart-change ${isPositive ? 'positive' : 'negative'}`}>
            {isPositive ? '+' : ''}{stock.change.toFixed(2)} ({isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%)
          </span>
        </div>
        <div className="chart-timeframes">
          {['1D', '1W', '1M', '3M'].map(tf => (
            <button
              key={tf}
              className={`timeframe-btn ${timeframe === tf ? 'active' : ''}`}
              onClick={() => setTimeframe(tf)}
            >
              {tf}
            </button>
          ))}
        </div>
        <button className="chart-close-btn" onClick={onClose}>
          <X size={20} />
        </button>
      </div>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={isPositive ? '#4ade80' : '#f87171'} stopOpacity={0.3} />
                <stop offset="100%" stopColor={isPositive ? '#4ade80' : '#f87171'} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
              dataKey={dataKey} 
              stroke="rgba(255,255,255,0.3)" 
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis 
              domain={[minPrice, maxPrice]}
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
              tickLine={false}
              axisLine={false}
              width={60}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={avgPrice} stroke="rgba(255,255,255,0.2)" strokeDasharray="5 5" />
            <Area
              type="monotone"
              dataKey="price"
              stroke={isPositive ? '#4ade80' : '#f87171'}
              strokeWidth={2}
              fill="url(#chartGradient)"
              dot={false}
              activeDot={{ r: 6, stroke: isPositive ? '#4ade80' : '#f87171', strokeWidth: 2, fill: '#050608' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-stats-row">
        <div className="chart-stat">
          <span className="chart-stat-label">Open</span>
          <span className="chart-stat-value">${(stock.price - stock.change).toFixed(2)}</span>
        </div>
        <div className="chart-stat">
          <span className="chart-stat-label">High</span>
          <span className="chart-stat-value positive">${stock.high.toFixed(2)}</span>
        </div>
        <div className="chart-stat">
          <span className="chart-stat-label">Low</span>
          <span className="chart-stat-value negative">${stock.low.toFixed(2)}</span>
        </div>
        <div className="chart-stat">
          <span className="chart-stat-label">Volume</span>
          <span className="chart-stat-value">{stock.volume}</span>
        </div>
        <div className="chart-stat">
          <span className="chart-stat-label">Avg Price</span>
          <span className="chart-stat-value">${avgPrice.toFixed(2)}</span>
        </div>
      </div>
    </motion.div>
  )
}

// News Item Component
function NewsItem({ news, delay }) {
  return (
    <motion.div
      className="news-item"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ x: 4 }}
    >
      <div className={`news-sentiment ${news.sentiment}`}>
        {news.sentiment === 'bullish' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
      </div>
      <div className="news-content">
        <p className="news-title">{news.title}</p>
        <div className="news-meta">
          <span className="news-source">{news.source}</span>
          <span className="news-time">{news.time}</span>
        </div>
      </div>
      <ChevronRight size={16} className="news-arrow" />
    </motion.div>
  )
}

// Main Market Overview Component
function MarketOverview() {
  const navigate = useNavigate()
  const [stocks, setStocks] = useState(initialStocks)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [isLive, setIsLive] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStock, setSelectedStock] = useState(null)

  // Simulate real-time price updates
  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(() => {
      setStocks(prev => prev.map(stock => {
        const newPrice = generatePrice(stock.price, 0.003)
        const newChange = newPrice - (stock.price - stock.change)
        const newChangePercent = (newChange / (stock.price - stock.change)) * 100
        return {
          ...stock,
          price: newPrice,
          change: newChange,
          changePercent: newChangePercent,
          high: Math.max(stock.high, newPrice),
          low: Math.min(stock.low, newPrice)
        }
      }))
      setLastUpdate(new Date())
    }, 3000)

    return () => clearInterval(interval)
  }, [isLive])

  const filteredStocks = useMemo(() => {
    if (!searchQuery) return stocks
    return stocks.filter(s => 
      s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [stocks, searchQuery])

  const marketSummary = useMemo(() => {
    const advancing = stocks.filter(s => s.change >= 0).length
    const declining = stocks.length - advancing
    const avgChange = stocks.reduce((acc, s) => acc + s.changePercent, 0) / stocks.length
    return { advancing, declining, avgChange }
  }, [stocks])

  return (
    <div className="market-overview">
      {/* Sidebar Navigation */}
      <Sidebar />
      
      {/* Main Wrapper */}
      <div className="market-main-wrapper">
        {/* Header */}
        <header className="overview-header">
          <div className="header-left">
            <h1>Market Overview</h1>
          </div>

          <div className="header-center">
            <div className="search-bar">
              <Search size={18} />
              <input
                type="text"
                placeholder="Search stocks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="header-right">
            <div className={`live-indicator ${isLive ? 'active' : ''}`} onClick={() => setIsLive(!isLive)}>
              <span className="live-dot" />
              <span>{isLive ? 'LIVE' : 'PAUSED'}</span>
            </div>
            <span className="last-update">
              <Clock size={14} />
              {lastUpdate.toLocaleTimeString()}
            </span>
            <button className="icon-btn">
              <Bell size={20} />
            </button>
            <button className="icon-btn" onClick={() => navigate('/dashboard')}>
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main className="overview-content">
          {/* Market Indices */}
          <section className="indices-section">
            <div className="section-header">
              <Globe size={20} />
              <h2>Market Indices</h2>
          </div>
          <div className="indices-grid">
            {indices.map((idx, i) => (
              <IndexCard key={idx.symbol} index={idx} delay={i * 0.1} />
            ))}
          </div>
        </section>

        {/* Market Summary */}
        <section className="summary-section">
          <div className="summary-cards">
            <motion.div 
              className="summary-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="summary-icon positive">
                <TrendingUp size={24} />
              </div>
              <div className="summary-info">
                <span className="summary-value">{marketSummary.advancing}</span>
                <span className="summary-label">Advancing</span>
              </div>
            </motion.div>

            <motion.div 
              className="summary-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="summary-icon negative">
                <TrendingDown size={24} />
              </div>
              <div className="summary-info">
                <span className="summary-value">{marketSummary.declining}</span>
                <span className="summary-label">Declining</span>
              </div>
            </motion.div>

            <motion.div 
              className="summary-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="summary-icon neutral">
                <Percent size={24} />
              </div>
              <div className="summary-info">
                <span className={`summary-value ${marketSummary.avgChange >= 0 ? 'positive' : 'negative'}`}>
                  {marketSummary.avgChange >= 0 ? '+' : ''}{marketSummary.avgChange.toFixed(2)}%
                </span>
                <span className="summary-label">Avg Change</span>
              </div>
            </motion.div>

            <motion.div 
              className="summary-card clickable"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              onClick={() => navigate('/dashboard')}
              whileHover={{ scale: 1.02 }}
            >
              <div className="summary-icon accent">
                <Activity size={24} />
              </div>
              <div className="summary-info">
                <span className="summary-value">Tools</span>
                <span className="summary-label">Open Dashboard</span>
              </div>
              <ChevronRight size={20} className="summary-arrow" />
            </motion.div>
          </div>
        </section>

        {/* Stock Detail Chart */}
        <AnimatePresence>
          {selectedStock && (
            <StockDetailChart 
              stock={selectedStock} 
              onClose={() => setSelectedStock(null)} 
            />
          )}
        </AnimatePresence>

        <div className="content-grid">
          {/* Stocks Section */}
          <section className="stocks-section">
            <div className="section-header">
              <BarChart3 size={20} />
              <h2>Top Stocks</h2>
              <span className="stock-count">{filteredStocks.length} stocks</span>
            </div>
            <div className="stocks-grid">
              {filteredStocks.map((stock, i) => (
                <StockCard 
                  key={stock.symbol} 
                  stock={stock} 
                  index={i} 
                  onSelect={setSelectedStock}
                  isSelected={selectedStock?.symbol === stock.symbol}
                />
              ))}
            </div>
          </section>

          {/* Right Sidebar */}
          <aside className="overview-sidebar">
            {/* Sector Performance */}
            <div className="sidebar-card">
              <div className="sidebar-header">
                <PieChart size={18} />
                <h3>Sector Performance</h3>
              </div>
              <div className="sector-list">
                {sectorPerformance.map((sector, i) => (
                  <motion.div
                    key={sector.name}
                    className="sector-item"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <span className="sector-name">{sector.name}</span>
                    <div className="sector-bar-container">
                      <motion.div
                        className="sector-bar"
                        style={{ backgroundColor: sector.color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(Math.abs(sector.change) * 20, 100)}%` }}
                        transition={{ delay: i * 0.05 + 0.3, duration: 0.5 }}
                      />
                    </div>
                    <span className={`sector-change ${sector.change >= 0 ? 'positive' : 'negative'}`}>
                      {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(2)}%
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Market News */}
            <div className="sidebar-card news-card">
              <div className="sidebar-header">
                <Newspaper size={18} />
                <h3>Market News</h3>
              </div>
              <div className="news-list">
                {marketNews.map((news, i) => (
                  <NewsItem key={news.id} news={news} delay={i * 0.1} />
                ))}
              </div>
            </div>
          </aside>
        </div>
      </main>
      </div>
    </div>
  )
}

export default MarketOverview
