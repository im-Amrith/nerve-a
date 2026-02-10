import { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float } from '@react-three/drei'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Shield, 
  Brain, 
  BookOpen, 
  TrendingUp, 
  ChevronDown,
  Zap,
  Lock,
  BarChart3,
  ArrowUpRight,
  Play
} from 'lucide-react'
import * as THREE from 'three'
import './LandingPage.css'

// Floating Stock Nodes Data
const stockNodes = [
  { symbol: 'NVDA', price: '875.42', x: 12, y: 18, change: '+2.4%', positive: true },
  { symbol: 'TSLA', price: '417.89', x: 85, y: 22, change: '+1.8%', positive: true },
  { symbol: 'AAPL', price: '198.45', x: 8, y: 65, change: '-0.6%', positive: false },
  { symbol: 'SPY', price: '512.34', x: 88, y: 72, change: '+0.9%', positive: true },
  { symbol: 'MSFT', price: '425.12', x: 18, y: 85, change: '+1.2%', positive: true },
  { symbol: 'GOOGL', price: '175.67', x: 78, y: 88, change: '-0.3%', positive: false },
]

// Floating Stock Node Component
function StockNode({ symbol, price, x, y, change, positive, delay }) {
  return (
    <motion.div
      className="stock-node"
      style={{ left: `${x}%`, top: `${y}%` }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay: delay * 0.15 + 0.5 }}
    >
      <motion.div 
        className="node-content"
        animate={{ 
          y: [0, -8, 0],
        }}
        transition={{ 
          duration: 4 + delay, 
          repeat: Infinity, 
          ease: "easeInOut" 
        }}
      >
        <div className="node-dot" />
        <div className="node-info">
          <span className="node-symbol">{symbol}</span>
          <span className="node-price">${price}</span>
          <span className={`node-change ${positive ? 'up' : 'down'}`}>{change}</span>
        </div>
      </motion.div>
      <div className="node-line" />
    </motion.div>
  )
}

// Ambient Floating Particles (subtle, organic)
function AmbientParticles({ count = 80 }) {
  const mesh = useRef()
  
  const particles = useMemo(() => {
    const temp = []
    for (let i = 0; i < count; i++) {
      temp.push({
        x: (Math.random() - 0.5) * 60,
        y: (Math.random() - 0.5) * 40,
        z: (Math.random() - 0.5) * 30,
        speed: 0.002 + Math.random() * 0.005,
        offset: Math.random() * Math.PI * 2
      })
    }
    return temp
  }, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    particles.forEach((p, i) => {
      dummy.position.set(
        p.x + Math.sin(time * p.speed * 100 + p.offset) * 2,
        p.y + Math.cos(time * p.speed * 80 + p.offset) * 1.5,
        p.z + Math.sin(time * p.speed * 60) * 1
      )
      dummy.scale.setScalar(0.08 + Math.sin(time + p.offset) * 0.03)
      dummy.updateMatrix()
      mesh.current.setMatrixAt(i, dummy.matrix)
    })
    mesh.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={mesh} args={[null, null, count]}>
      <sphereGeometry args={[1, 8, 8]} />
      <meshBasicMaterial color="#ffffff" transparent opacity={0.4} />
    </instancedMesh>
  )
}

// Slow moving gradient orb
function GradientOrb() {
  const meshRef = useRef()
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime() * 0.15
    meshRef.current.position.x = Math.sin(t) * 3
    meshRef.current.position.y = Math.cos(t * 0.7) * 2
    meshRef.current.rotation.z = t * 0.1
  })

  return (
    <mesh ref={meshRef} position={[0, 0, -15]}>
      <sphereGeometry args={[12, 32, 32]} />
      <meshBasicMaterial 
        color="#1a4a5c"
        transparent 
        opacity={0.5}
      />
    </mesh>
  )
}

// Feature Card Component
function FeatureCard({ icon: Icon, title, description, delay }) {
  return (
    <motion.div
      className="feature-card"
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
      whileHover={{ scale: 1.02, y: -5 }}
    >
      <div className="feature-icon">
        <Icon size={28} strokeWidth={1.5} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
    </motion.div>
  )
}

// Main Landing Page Component
function LandingPage() {
  const navigate = useNavigate()
  const [currentSlide, setCurrentSlide] = useState(1)

  const scrollToFeatures = () => {
    document.getElementById('features').scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="landing-page">
      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-brand">
          <div className="brand-icon nerve-brand">
            <Zap size={20} />
          </div>
          <span>NERVE</span>
        </div>
        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#how">How it works</a>
          <a href="#about">About</a>
        </div>
        <button className="nav-cta" onClick={() => navigate('/markets')}>
          Open App <ArrowUpRight size={16} />
        </button>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        {/* 3D Background */}
        <div className="canvas-container">
          <Canvas camera={{ position: [0, 0, 30], fov: 50 }}>
            <ambientLight intensity={0.3} />
            <AmbientParticles count={60} />
            <GradientOrb />
          </Canvas>
        </div>

        {/* Central Glow Effect */}
        <div className="hero-glow" />
        <div className="hero-glow secondary" />

        {/* Floating Stock Nodes */}
        {stockNodes.map((node, i) => (
          <StockNode key={node.symbol} {...node} delay={i} />
        ))}

        {/* Hero Content */}
        <div className="hero-content">
          <motion.div
            className="hero-badge system-badge"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="status-dot"></span> SYSTEM ONLINE_v2.4
          </motion.div>

          <motion.h1
            className="nerve-title"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.15 }}
          >
            NERVE
          </motion.h1>

          <motion.div
            className="nerve-tagline"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.25 }}
          >
            <span className="tagline-bracket">[</span>
            <span className="tagline-text">THE AGENTIC BROKERAGE OS</span>
            <span className="tagline-bracket">]</span>
          </motion.div>

          <motion.p
            className="hero-subtitle"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Your broker executes. <strong>Nerve thinks.</strong>
          </motion.p>

          <motion.div
            className="hero-buttons"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.45 }}
          >
            <button className="btn-primary" onClick={() => navigate('/markets')}>
              Open App <ArrowUpRight size={18} />
            </button>
            <button className="btn-secondary" onClick={scrollToFeatures}>
              Discover More
            </button>
          </motion.div>

          <motion.div
            className="hero-video-btn"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <div className="play-btn">
              <Play size={16} fill="white" />
            </div>
          </motion.div>
        </div>

        {/* Slide Indicator */}
        <div className="slide-indicator">
          <ChevronDown size={18} />
          <span>01/03 . Scroll down</span>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="section-label">Core Features</span>
          <h2>Four Pillars of<br/><span className="gradient-text">Intelligent Trading</span></h2>
        </motion.div>

        <div className="features-grid">
          <FeatureCard
            icon={Shield}
            title="Pre-Trade Sentinel"
            description="Real-time safety checks with sub-50ms latency. Your AI kill switch enforcing rules before orders hit the exchange."
            delay={0.1}
          />
          <FeatureCard
            icon={Brain}
            title="Strategy Engine"
            description="Describe strategies in plain English. AI generates, backtests, and validates trading algorithms instantly."
            delay={0.2}
          />
          <FeatureCard
            icon={BookOpen}
            title="RAG Journaling"
            description="Every trade gets an AI autopsy. Semantic search reveals hidden patterns in your trading history."
            delay={0.3}
          />
          <FeatureCard
            icon={TrendingUp}
            title="Intelligence Layer"
            description="A swarm of specialized agents gather news, sentiment, technicals, and volatility in parallel."
            delay={0.4}
          />
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <motion.div
          className="stats-grid"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <div className="stat-item">
            <span className="stat-number">&lt;50ms</span>
            <span className="stat-label">Sentinel Latency</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">4</span>
            <span className="stat-label">AI Agents</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">100%</span>
            <span className="stat-label">Trade Protection</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">∞</span>
            <span className="stat-label">Strategies</span>
          </div>
        </motion.div>
      </section>

      {/* How It Works Section */}
      <section id="how" className="how-section">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="section-label">Workflow</span>
          <h2>How It <span className="gradient-text">Works</span></h2>
        </motion.div>

        <div className="how-grid">
          <motion.div
            className="how-step"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            <div className="step-number">01</div>
            <div className="step-content">
              <Lock size={22} strokeWidth={1.5} />
              <h3>Define Your Constitution</h3>
              <p>Set position limits, loss thresholds, and trading rules. The Sentinel enforces automatically.</p>
            </div>
          </motion.div>

          <motion.div
            className="how-step"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <div className="step-number">02</div>
            <div className="step-content">
              <Brain size={22} strokeWidth={1.5} />
              <h3>Generate Strategies</h3>
              <p>Describe your trading idea in plain English. AI creates and backtests the implementation.</p>
            </div>
          </motion.div>

          <motion.div
            className="how-step"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            <div className="step-number">03</div>
            <div className="step-content">
              <BarChart3 size={22} strokeWidth={1.5} />
              <h3>Gather Intelligence</h3>
              <p>Multi-agent swarm analyzes markets in real-time. Institutional-grade insights for every trader.</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="about" className="cta-section">
        <motion.div
          className="cta-glow"
          animate={{ 
            opacity: [0.3, 0.5, 0.3],
            scale: [1, 1.1, 1]
          }}
          transition={{ duration: 4, repeat: Infinity }}
        />
        <motion.div
          className="cta-content"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2>Ready to Trade Smarter?</h2>
          <p>Experience the future of retail trading with AI-powered protection and intelligence.</p>
          <button className="btn-primary large" onClick={() => navigate('/dashboard')}>
            Enter the Dashboard <ArrowUpRight size={18} />
          </button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="brand-icon small">
              <Zap size={16} />
            </div>
            <span>Agentic Brokerage OS</span>
          </div>
          <div className="footer-info">
            <span>Built with Groq • FastAPI • React Three Fiber</span>
          </div>
          <div className="footer-links">
            <span>Hackathon 2026</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
