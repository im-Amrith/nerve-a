import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Zap,
  Activity,
  Shield,
  Brain,
  BookOpen,
  TrendingUp,
  Home,
  Briefcase,
  PlayCircle,
  Settings as SettingsIcon,
  User,
  Bell,
  Palette,
  Lock,
  Database,
  Globe,
  Moon,
  Sun,
  Monitor,
  Volume2,
  Mail,
  Smartphone,
  Key,
  RefreshCw,
  Save,
  Check,
  AlertTriangle,
  Info,
  ChevronRight
} from 'lucide-react'
import './Settings.css'

// Sidebar Navigation
function Sidebar() {
  const navigate = useNavigate()
  
  const tabs = [
    { id: 'overview', icon: Activity, label: 'Overview', route: '/markets' },
    { id: 'sentinel', icon: Shield, label: 'Sentinel', route: '/dashboard' },
    { id: 'strategy', icon: Brain, label: 'Strategy', route: '/dashboard' },
    { id: 'journal', icon: BookOpen, label: 'Journal', route: '/dashboard' },
    { id: 'intelligence', icon: TrendingUp, label: 'Intelligence', route: '/dashboard' },
    { id: 'portfolio', icon: Briefcase, label: 'Portfolio', route: '/portfolio' },
    { id: 'simulation', icon: PlayCircle, label: 'Simulation', route: '/simulation' },
    { id: 'settings', icon: SettingsIcon, label: 'Settings', route: '/settings' },
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
            className={`nav-item ${tab.id === 'settings' ? 'active' : ''}`}
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

// Toggle Switch Component
function ToggleSwitch({ enabled, onChange }) {
  return (
    <button 
      className={`toggle-switch ${enabled ? 'enabled' : ''}`}
      onClick={() => onChange(!enabled)}
    >
      <span className="toggle-slider" />
    </button>
  )
}

function Settings() {
  const navigate = useNavigate()
  const [activeSection, setActiveSection] = useState('profile')
  const [isSaving, setIsSaving] = useState(false)
  const [showSaved, setShowSaved] = useState(false)
  
  // Settings state
  const [settings, setSettings] = useState({
    // Profile
    displayName: 'Trader',
    email: 'trader@nerve.ai',
    timezone: 'America/New_York',
    
    // Appearance
    theme: 'dark',
    accentColor: 'blue',
    compactMode: false,
    animationsEnabled: true,
    
    // Notifications
    emailAlerts: true,
    pushNotifications: true,
    tradeAlerts: true,
    marketNews: true,
    priceAlerts: true,
    weeklyDigest: false,
    soundEnabled: true,
    
    // Trading
    defaultQuantity: 100,
    confirmTrades: true,
    riskWarnings: true,
    autoRefresh: true,
    refreshInterval: 30,
    
    // API & Data
    apiKey: '••••••••••••••••',
    dataProvider: 'yahoo',
    historicalDays: 365,
    cacheEnabled: true,
    
    // Privacy
    analyticsEnabled: true,
    crashReports: true,
    usageData: false,
  })

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsSaving(false)
    setShowSaved(true)
    setTimeout(() => setShowSaved(false), 2000)
  }

  const sections = [
    { id: 'profile', icon: User, label: 'Profile' },
    { id: 'appearance', icon: Palette, label: 'Appearance' },
    { id: 'notifications', icon: Bell, label: 'Notifications' },
    { id: 'trading', icon: TrendingUp, label: 'Trading' },
    { id: 'api', icon: Database, label: 'API & Data' },
    { id: 'privacy', icon: Lock, label: 'Privacy' },
  ]

  return (
    <div className="settings-page">
      <Sidebar />
      
      <main className="settings-main">
        {/* Hero Header */}
        <div className="settings-hero">
          <div className="settings-hero-content">
            <h1 className="settings-title">SETTINGS</h1>
            <p className="settings-subtitle">Customize your NERVE trading experience</p>
          </div>
          <button 
            className={`btn-save ${showSaved ? 'saved' : ''}`} 
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? (
              <>
                <RefreshCw className="spin" size={18} />
                Saving...
              </>
            ) : showSaved ? (
              <>
                <Check size={18} />
                Saved!
              </>
            ) : (
              <>
                <Save size={18} />
                Save Changes
              </>
            )}
          </button>
        </div>

        <div className="settings-layout">
          {/* Settings Navigation */}
          <nav className="settings-nav">
            {sections.map(section => (
              <button
                key={section.id}
                className={`settings-nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id)}
              >
                <section.icon size={18} />
                <span>{section.label}</span>
                <ChevronRight size={16} className="chevron" />
              </button>
            ))}
          </nav>

          {/* Settings Content */}
          <div className="settings-content">
            {/* Profile Section */}
            {activeSection === 'profile' && (
              <motion.div 
                className="settings-section"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="section-header">
                  <User size={22} />
                  <div>
                    <h2>Profile Settings</h2>
                    <p>Manage your account information</p>
                  </div>
                </div>

                <div className="settings-group">
                  <div className="setting-item">
                    <label>Display Name</label>
                    <input
                      type="text"
                      value={settings.displayName}
                      onChange={(e) => updateSetting('displayName', e.target.value)}
                      placeholder="Your name"
                    />
                  </div>

                  <div className="setting-item">
                    <label>Email Address</label>
                    <input
                      type="email"
                      value={settings.email}
                      onChange={(e) => updateSetting('email', e.target.value)}
                      placeholder="your@email.com"
                    />
                  </div>

                  <div className="setting-item">
                    <label>Timezone</label>
                    <select 
                      value={settings.timezone}
                      onChange={(e) => updateSetting('timezone', e.target.value)}
                    >
                      <option value="America/New_York">Eastern Time (ET)</option>
                      <option value="America/Chicago">Central Time (CT)</option>
                      <option value="America/Denver">Mountain Time (MT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PT)</option>
                      <option value="Europe/London">London (GMT)</option>
                      <option value="Europe/Paris">Central European (CET)</option>
                      <option value="Asia/Tokyo">Tokyo (JST)</option>
                      <option value="Asia/Kolkata">India (IST)</option>
                    </select>
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Account Actions</h3>
                  <div className="action-buttons">
                    <button className="btn-action">
                      <Key size={16} />
                      Change Password
                    </button>
                    <button className="btn-action danger">
                      <AlertTriangle size={16} />
                      Delete Account
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Appearance Section */}
            {activeSection === 'appearance' && (
              <motion.div 
                className="settings-section"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="section-header">
                  <Palette size={22} />
                  <div>
                    <h2>Appearance</h2>
                    <p>Customize how NERVE looks</p>
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Theme</h3>
                  <div className="theme-options">
                    <button 
                      className={`theme-option ${settings.theme === 'dark' ? 'active' : ''}`}
                      onClick={() => updateSetting('theme', 'dark')}
                    >
                      <Moon size={24} />
                      <span>Dark</span>
                    </button>
                    <button 
                      className={`theme-option ${settings.theme === 'light' ? 'active' : ''}`}
                      onClick={() => updateSetting('theme', 'light')}
                    >
                      <Sun size={24} />
                      <span>Light</span>
                    </button>
                    <button 
                      className={`theme-option ${settings.theme === 'system' ? 'active' : ''}`}
                      onClick={() => updateSetting('theme', 'system')}
                    >
                      <Monitor size={24} />
                      <span>System</span>
                    </button>
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Accent Color</h3>
                  <div className="color-options">
                    {['blue', 'purple', 'green', 'orange', 'pink', 'cyan'].map(color => (
                      <button
                        key={color}
                        className={`color-option ${color} ${settings.accentColor === color ? 'active' : ''}`}
                        onClick={() => updateSetting('accentColor', color)}
                      />
                    ))}
                  </div>
                </div>

                <div className="settings-group">
                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Compact Mode</span>
                      <span className="setting-desc">Reduce spacing for more content</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.compactMode}
                      onChange={(v) => updateSetting('compactMode', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Animations</span>
                      <span className="setting-desc">Enable smooth transitions</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.animationsEnabled}
                      onChange={(v) => updateSetting('animationsEnabled', v)}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {/* Notifications Section */}
            {activeSection === 'notifications' && (
              <motion.div 
                className="settings-section"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="section-header">
                  <Bell size={22} />
                  <div>
                    <h2>Notifications</h2>
                    <p>Control how you receive alerts</p>
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Channels</h3>
                  <div className="setting-row">
                    <div className="setting-info">
                      <Mail size={18} />
                      <div>
                        <span className="setting-label">Email Alerts</span>
                        <span className="setting-desc">Receive notifications via email</span>
                      </div>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.emailAlerts}
                      onChange={(v) => updateSetting('emailAlerts', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <Smartphone size={18} />
                      <div>
                        <span className="setting-label">Push Notifications</span>
                        <span className="setting-desc">Browser push notifications</span>
                      </div>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.pushNotifications}
                      onChange={(v) => updateSetting('pushNotifications', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <Volume2 size={18} />
                      <div>
                        <span className="setting-label">Sound Effects</span>
                        <span className="setting-desc">Play sounds for alerts</span>
                      </div>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.soundEnabled}
                      onChange={(v) => updateSetting('soundEnabled', v)}
                    />
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Alert Types</h3>
                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Trade Alerts</span>
                      <span className="setting-desc">Execution and order updates</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.tradeAlerts}
                      onChange={(v) => updateSetting('tradeAlerts', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Price Alerts</span>
                      <span className="setting-desc">When stocks hit target prices</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.priceAlerts}
                      onChange={(v) => updateSetting('priceAlerts', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Market News</span>
                      <span className="setting-desc">Breaking news and updates</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.marketNews}
                      onChange={(v) => updateSetting('marketNews', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Weekly Digest</span>
                      <span className="setting-desc">Summary of your trading week</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.weeklyDigest}
                      onChange={(v) => updateSetting('weeklyDigest', v)}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {/* Trading Section */}
            {activeSection === 'trading' && (
              <motion.div 
                className="settings-section"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="section-header">
                  <TrendingUp size={22} />
                  <div>
                    <h2>Trading Preferences</h2>
                    <p>Configure your trading defaults</p>
                  </div>
                </div>

                <div className="settings-group">
                  <div className="setting-item">
                    <label>Default Quantity</label>
                    <input
                      type="number"
                      value={settings.defaultQuantity}
                      onChange={(e) => updateSetting('defaultQuantity', parseInt(e.target.value) || 0)}
                      min="1"
                    />
                  </div>

                  <div className="setting-item">
                    <label>Auto-Refresh Interval</label>
                    <select 
                      value={settings.refreshInterval}
                      onChange={(e) => updateSetting('refreshInterval', parseInt(e.target.value))}
                    >
                      <option value="5">5 seconds</option>
                      <option value="10">10 seconds</option>
                      <option value="30">30 seconds</option>
                      <option value="60">1 minute</option>
                      <option value="300">5 minutes</option>
                    </select>
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Safety Features</h3>
                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Confirm Trades</span>
                      <span className="setting-desc">Require confirmation before executing</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.confirmTrades}
                      onChange={(v) => updateSetting('confirmTrades', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Risk Warnings</span>
                      <span className="setting-desc">Show warnings for risky trades</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.riskWarnings}
                      onChange={(v) => updateSetting('riskWarnings', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Auto-Refresh Data</span>
                      <span className="setting-desc">Keep market data up to date</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.autoRefresh}
                      onChange={(v) => updateSetting('autoRefresh', v)}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {/* API & Data Section */}
            {activeSection === 'api' && (
              <motion.div 
                className="settings-section"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="section-header">
                  <Database size={22} />
                  <div>
                    <h2>API & Data</h2>
                    <p>Manage data sources and API keys</p>
                  </div>
                </div>

                <div className="settings-group">
                  <div className="setting-item">
                    <label>API Key</label>
                    <div className="api-key-input">
                      <input
                        type="password"
                        value={settings.apiKey}
                        onChange={(e) => updateSetting('apiKey', e.target.value)}
                        placeholder="Enter your API key"
                      />
                      <button className="btn-reveal">Show</button>
                    </div>
                  </div>

                  <div className="setting-item">
                    <label>Data Provider</label>
                    <select 
                      value={settings.dataProvider}
                      onChange={(e) => updateSetting('dataProvider', e.target.value)}
                    >
                      <option value="yahoo">Yahoo Finance</option>
                      <option value="alphavantage">Alpha Vantage</option>
                      <option value="polygon">Polygon.io</option>
                      <option value="finnhub">Finnhub</option>
                    </select>
                  </div>

                  <div className="setting-item">
                    <label>Historical Data Days</label>
                    <select 
                      value={settings.historicalDays}
                      onChange={(e) => updateSetting('historicalDays', parseInt(e.target.value))}
                    >
                      <option value="30">30 days</option>
                      <option value="90">90 days</option>
                      <option value="180">180 days</option>
                      <option value="365">1 year</option>
                      <option value="730">2 years</option>
                    </select>
                  </div>
                </div>

                <div className="settings-group">
                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Cache Data</span>
                      <span className="setting-desc">Store data locally for faster loading</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.cacheEnabled}
                      onChange={(v) => updateSetting('cacheEnabled', v)}
                    />
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Data Management</h3>
                  <div className="action-buttons">
                    <button className="btn-action">
                      <RefreshCw size={16} />
                      Clear Cache
                    </button>
                    <button className="btn-action">
                      <Database size={16} />
                      Export Data
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Privacy Section */}
            {activeSection === 'privacy' && (
              <motion.div 
                className="settings-section"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="section-header">
                  <Lock size={22} />
                  <div>
                    <h2>Privacy & Security</h2>
                    <p>Control your data and privacy</p>
                  </div>
                </div>

                <div className="settings-group">
                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Analytics</span>
                      <span className="setting-desc">Help improve NERVE with usage data</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.analyticsEnabled}
                      onChange={(v) => updateSetting('analyticsEnabled', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Crash Reports</span>
                      <span className="setting-desc">Automatically send error reports</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.crashReports}
                      onChange={(v) => updateSetting('crashReports', v)}
                    />
                  </div>

                  <div className="setting-row">
                    <div className="setting-info">
                      <span className="setting-label">Usage Statistics</span>
                      <span className="setting-desc">Share feature usage data</span>
                    </div>
                    <ToggleSwitch 
                      enabled={settings.usageData}
                      onChange={(v) => updateSetting('usageData', v)}
                    />
                  </div>
                </div>

                <div className="settings-group">
                  <h3>Data Control</h3>
                  <div className="action-buttons">
                    <button className="btn-action">
                      <Database size={16} />
                      Download My Data
                    </button>
                    <button className="btn-action danger">
                      <AlertTriangle size={16} />
                      Delete All Data
                    </button>
                  </div>
                </div>

                <div className="privacy-notice">
                  <Info size={16} />
                  <p>Your data is encrypted and stored securely. We never sell your personal information to third parties.</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default Settings
