import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import MarketOverview from './pages/MarketOverview'
import Dashboard from './pages/Dashboard'
import Portfolio from './pages/Portfolio'
import Simulation from './pages/Simulation'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/markets" element={<MarketOverview />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/simulation" element={<Simulation />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
