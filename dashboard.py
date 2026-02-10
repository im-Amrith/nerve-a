"""
Agentic Brokerage OS - Interactive Dashboard
Beautiful UI to demonstrate all 4 core features to judges.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime
import time
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.engines.pre_trade_sentinel import PreTradeSentinel
from src.engines.strategy_engine import StrategyEngine
from src.engines.rag_journal import RAGJournal
from src.engines.retail_intelligence import RetailIntelligenceLayer
from src.core.orchestrator import Orchestrator
from src.core.state import (
    UserConstitution, 
    TradeIntent, 
    TradeExecution,
    SentinelResult
)

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="Agentic Brokerage OS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern Glassmorphism & 3D Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b4e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated Background Particles */
    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px); }
        33% { transform: translateY(-20px) translateX(10px); }
        66% { transform: translateY(10px) translateX(-10px); }
    }
    
    @keyframes glow-pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    
    /* Main Header with 3D Effect */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 2rem 1rem;
        letter-spacing: -0.02em;
        position: relative;
        text-shadow: none;
        animation: title-glow 3s ease-in-out infinite;
        transform: perspective(500px) rotateX(2deg);
    }
    
    @keyframes title-glow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(79, 172, 254, 0.3)); }
        50% { filter: drop-shadow(0 0 40px rgba(168, 85, 247, 0.5)); }
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 8px 32px 0 rgba(0, 0, 0, 0.37),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        transform: translateZ(0);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
        transition: left 0.6s;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) translateZ(20px);
        box-shadow: 
            0 20px 60px 0 rgba(79, 172, 254, 0.2),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(79, 172, 254, 0.3);
    }
    
    /* Feature Cards with 3D Depth */
    .feature-card {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin: 1.5rem 0;
        position: relative;
        transform-style: preserve-3d;
        transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-10px) rotateX(5deg) rotateY(-5deg);
        box-shadow: 
            0 25px 70px rgba(79, 172, 254, 0.25),
            inset 0 2px 0 rgba(255, 255, 255, 0.15);
    }
    
    /* Metric Cards with 3D Animation */
    .metric-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(79, 172, 254, 0.3);
        border-left: 4px solid #4facfe;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(79, 172, 254, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .metric-card:hover::after {
        opacity: 1;
        animation: rotate-glow 4s linear infinite;
    }
    
    @keyframes rotate-glow {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .metric-card:hover {
        transform: translateZ(10px) scale(1.02);
        border-left-color: #a855f7;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.2);
    }
    
    /* Success/Danger Boxes with Glassmorphism */
    .success-box {
        background: rgba(16, 185, 129, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #10b981;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
        transform: translateZ(0);
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .success-box b {
        color: #34d399 !important;
        font-weight: 700 !important;
    }
    
    .success-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(16, 185, 129, 0.25);
    }
    
    .danger-box {
        background: rgba(239, 68, 68, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #ef4444;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.15);
        transform: translateZ(0);
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .danger-box b {
        color: #f87171 !important;
        font-weight: 700 !important;
    }
    
    /* Bold/Strong Text */
    strong, b {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
    }
    
    .danger-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(239, 68, 68, 0.25);
    }
    
    /* Agent Status Badges with 3D Effect */
    .agent-status {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        position: relative;
        transform-style: preserve-3d;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .agent-status:hover {
        transform: translateY(-3px) translateZ(10px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
    }
    
    .agent-active {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 
            0 4px 15px rgba(16, 185, 129, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    /* Code Block with Depth */
    .code-block {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        color: #e2e8f0;
        padding: 1.5rem;
        border-radius: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
        border: 1px solid rgba(79, 172, 254, 0.2);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        position: relative;
    }
    
    /* Streamlit Component Overrides */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
        box-shadow: 0 8px 24px rgba(79, 172, 254, 0.3);
        position: relative;
        overflow: hidden;
        transform: translateZ(0);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) translateZ(10px);
        box-shadow: 0 16px 48px rgba(79, 172, 254, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(0.98);
    }
    
    /* Button Text */
    .stButton > button p {
        color: white !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    
    /* Input Placeholder Text */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: rgba(241, 245, 249, 0.4) !important;
    }
    
    /* Input Values */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        color: #f1f5f9 !important;
        font-size: 0.95rem !important;
    }
    
    /* Text Input with Glassmorphism */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4facfe !important;
        box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1) !important;
        transform: translateY(-2px);
    }
    
    /* Selectbox with Depth */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        color: #f1f5f9 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.95) 0%, rgba(29, 27, 78, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(79, 172, 254, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        background: transparent;
        padding: 0;
        border-radius: 0;
        margin: 0;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        padding: 0.75rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid transparent;
        transition: all 0.3s ease;
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(79, 172, 254, 0.1);
        border-color: rgba(79, 172, 254, 0.3);
        transform: translateX(5px);
    }
    
    /* Radio Button Text */
    [data-testid="stSidebar"] .stRadio label p {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    
    /* Selected Radio Option */
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        background: rgba(79, 172, 254, 0.2) !important;
    }
    
    /* Metric Cards Enhancement */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4facfe 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-weight: 500 !important;
    }
    
    /* Metric Container */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(79, 172, 254, 0.2);
    }
    
    /* Expander with Glassmorphism */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        transition: all 0.3s ease !important;
        color: #f1f5f9 !important;
    }
    
    .streamlit-expanderContent {
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(79, 172, 254, 0.1) !important;
        border-color: rgba(79, 172, 254, 0.4) !important;
        transform: translateX(5px);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4facfe 0%, #a855f7 100%);
        border-radius: 10px;
        box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-color: #4facfe transparent transparent transparent !important;
    }
    
    /* Custom Loading Animation */
    @keyframes pulse-loading {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(1.05);
        }
    }
    
    /* Info/Warning/Success Message Boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
    }
    
    .stAlert > div {
        color: #f1f5f9 !important;
    }
    
    /* Success Messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-color: rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Error Messages */
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
    }
    
    /* Info Messages */
    .stInfo {
        background: rgba(79, 172, 254, 0.1) !important;
        border-color: rgba(79, 172, 254, 0.3) !important;
    }
    
    /* Warning Messages */
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border-color: rgba(251, 191, 36, 0.3) !important;
    }
    
    /* Better Text Styling */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
        letter-spacing: -0.01em;
    }
    
    p, li, span, div, label {
        color: #e2e8f0 !important;
    }
    
    /* Force Streamlit Labels to be Visible */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stRadio > label {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    /* Form Labels */
    label[data-testid="stWidgetLabel"] {
        color: #f1f5f9 !important;
    }
    
    /* Markdown Text */
    .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #e2e8f0 !important;
    }
    
    /* Markdown Links */
    a {
        color: #4facfe !important;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #00f2fe !important;
        text-shadow: 0 0 10px rgba(79, 172, 254, 0.5);
    }
    
    /* JSON Display */
    .stJson {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stJson pre {
        color: #f1f5f9 !important;
    }
    
    /* Code Blocks */
    code {
        background: rgba(79, 172, 254, 0.15) !important;
        color: #4facfe !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
    }
    
    pre {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    pre code {
        color: #e2e8f0 !important;
        background: transparent !important;
    }
    
    /* Dividers with Gradient */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(79, 172, 254, 0.5), transparent) !important;
        margin: 2rem 0 !important;
    }
    
    /* Spinner Text */
    .stSpinner > div > div {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    
    /* Dataframe/Table Text */
    .stDataFrame, .stTable {
        color: #f1f5f9 !important;
    }
    
    /* All Child Elements in Glass Cards */
    .glass-card * {
        color: inherit;
    }
    
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4 {
        color: #f1f5f9 !important;
    }
    
    .glass-card p, .glass-card li {
        color: #e2e8f0 !important;
    }
    /* Style Streamlit Containers as Glass Cards */
    .element-container {
        color: #e2e8f0 !important;
    }
    
    /* Column Containers - Only style when in feature sections */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="column"]:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(79, 172, 254, 0.2);
    }
    
    /* Remove box styling from vertical blocks - this was causing empty boxes */
    [data-testid="stVerticalBlock"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        backdrop-filter: none !important;
        border-radius: 0 !important;
    }
    
    /* Ensure All Text is Visible */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #f1f5f9 !important;
    }
    
    .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
        color: #e2e8f0 !important;
    }
    
    /* Container Blocks */
    .block-container {
        color: #e2e8f0 !important;
    }
    
    .block-container h1, .block-container h2, .block-container h3, .block-container h4 {
        color: #f1f5f9 !important;
    }
    
    .block-container p, .block-container li {
        color: #e2e8f0 !important;
    }


</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.groq_key = os.getenv("GROQ_API_KEY")
    st.session_state.news_key = os.getenv("NEWS_API_KEY")

def init_engines():
    """Initialize all engines"""
    if not st.session_state.groq_key:
        st.error("⚠️ GROQ_API_KEY not found! Please set it in .env file")
        return False
    
    try:
        constitution = UserConstitution(
            max_position_size=10000,
            max_daily_loss=500,
            blocked_symbols=["GME", "AMC"],
            trading_hours_only=False
        )
        
        st.session_state.sentinel = PreTradeSentinel(
            st.session_state.groq_key,
            constitution
        )
        st.session_state.strategy_engine = StrategyEngine(st.session_state.groq_key)
        st.session_state.journal = RAGJournal(
            st.session_state.groq_key,
            st.session_state.news_key
        )
        st.session_state.intelligence = RetailIntelligenceLayer(
            st.session_state.groq_key,
            st.session_state.news_key
        )
        st.session_state.orchestrator = Orchestrator(
            st.session_state.groq_key,
            constitution,
            st.session_state.news_key
        )
        
        st.session_state.initialized = True
        return True
    except Exception as e:
        st.error(f"❌ Initialization failed: {e}")
        return False

def render_header():
    """Render main header"""
    st.markdown('<h1 class="main-header">🤖 Agentic Brokerage OS</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem; color: rgba(226, 232, 240, 0.8); font-weight: 300; margin-top: -1rem; letter-spacing: 0.02em;">Intelligence-First Trading System with Autonomous AI Agents</p>', unsafe_allow_html=True)
    
    # Status indicators with spacing
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🛡️ Pre-Trade Sentinel", "Active", delta="<50ms")
    with col2:
        st.metric("🧠 Strategy Engine", "Ready", delta="LLM-Powered")
    with col3:
        st.metric("📝 RAG Journal", "Logging", delta="Context-Aware")
    with col4:
        st.metric("🌐 Intelligence Layer", "4 Agents", delta="Real-Time")

def render_sentinel_demo():
    """FR1: Pre-Trade Sentinel Demo"""
    st.markdown("### 🛡️ FR1: Pre-Trade Sentinel (<50ms Kill Switch)")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Test Trade Parameters")
        symbol = st.text_input("Symbol", "AAPL", key="sentinel_symbol")
        quantity = st.number_input("Quantity", min_value=1, value=10, key="sentinel_qty")
        action = st.selectbox("Action", ["buy", "sell"], key="sentinel_action")
        price = st.number_input("Price", min_value=0.01, value=150.0, key="sentinel_price")
        
        if st.button("🔍 Check Trade", key="check_trade_btn"):
            intent = TradeIntent(
                action=action,
                symbol=symbol,
                quantity=quantity,
                order_type="market",
                price=price,
                timestamp=datetime.now(),
                natural_language_prompt=f"{action} {quantity} shares of {symbol}"
            )
            
            start = time.perf_counter()
            result = st.session_state.sentinel.check_trade(intent, {"total_value": 100000})
            latency_ms = (time.perf_counter() - start) * 1000
            
            st.session_state.sentinel_result = result
            st.session_state.sentinel_latency = latency_ms
    
    with col2:
        st.markdown("#### Sentinel Result")
        
        if 'sentinel_result' in st.session_state:
            result = st.session_state.sentinel_result
            latency = st.session_state.sentinel_latency
            
            # Show latency
            if latency < 50:
                st.success(f"⚡ Latency: {latency:.2f}ms ({"✓ " if latency < 50 else "✗ "}Sub-50ms)")
            else:
                st.warning(f"⚡ Latency: {latency:.2f}ms (Edge case with LLM)")
            
            # Show decision
            if result.approved:
                st.markdown(f'<div class="success-box">✅ <b>APPROVED</b><br>{result.reasoning}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="danger-box">🚫 <b>BLOCKED</b><br>{result.reasoning}</div>', unsafe_allow_html=True)
            
            # Show metrics
            st.metric("Risk Score", f"{result.risk_score:.2f}/1.00")
            st.metric("Violations", len(result.violated_rules))
            
            if result.violated_rules:
                st.markdown("**Violated Rules:**")
                for rule in result.violated_rules:
                    st.markdown(f"- {rule}")

def render_strategy_demo():
    """FR2: Semantic Strategy Engine Demo"""
    st.markdown("### 🧠 FR2: Semantic Strategy Engine (NL → Code)")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Natural Language Strategy")
        nl_prompt = st.text_area(
            "Describe your trading strategy:",
            value="Buy when RSI is below 30 and MACD crosses above signal line. Sell when RSI goes above 70.",
            height=150,
            key="strategy_prompt"
        )
        
        # Symbol selection for backtesting with real data
        backtest_symbol = st.selectbox(
            "Backtest on real stock data:",
            ["SPY", "AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META"],
            key="backtest_symbol"
        )
        
        if st.button("🚀 Generate Strategy", key="gen_strategy_btn"):
            with st.spinner(f"🤖 Generating strategy and backtesting on {backtest_symbol}..."):
                try:
                    strategy = st.session_state.strategy_engine.generate_strategy(
                        natural_language_prompt=nl_prompt,
                        auto_backtest=True,
                        backtest_symbol=backtest_symbol
                    )
                    st.session_state.generated_strategy = strategy
                    st.success(f"✅ Strategy generated and backtested on {backtest_symbol}!")
                except Exception as e:
                    st.error(f"❌ Generation failed: {e}")
    
    with col2:
        st.markdown("#### Generated Strategy")
        
        if 'generated_strategy' in st.session_state:
            strategy = st.session_state.generated_strategy
            
            st.markdown(f"**Name:** `{strategy.name}`")
            st.markdown(f"**ID:** `{strategy.strategy_id}`")
            
            # Show backtest results
            if strategy.backtest_results:
                bt = strategy.backtest_results
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Sharpe Ratio", f"{bt.get('sharpe_ratio', 0):.2f}")
                col_b.metric("Total Return", f"{bt.get('total_return', 0):.2%}")
                col_c.metric("Total Trades", bt.get('total_trades', 0))
            
            # Show code preview
            with st.expander("📄 View Generated Code"):
                st.code(strategy.generated_code[:1000] + "...", language="python")

def render_journal_demo():
    """FR3: Contextual RAG Journaling Demo"""
    st.markdown("### 📝 FR3: Contextual RAG Journaling (Trade Autopsy)")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Simulated Trade")
        symbol = st.text_input("Symbol", "TSLA", key="journal_symbol")
        
        # Fetch live price button
        col_price, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("📈 Live", key="fetch_price_btn", help="Fetch current market price"):
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    live_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                    if live_price > 0:
                        st.session_state.live_entry_price = float(live_price)
                        st.session_state.live_exit_price = float(live_price * 1.04)  # 4% profit target
                except Exception as e:
                    st.error(f"Failed: {e}")
        
        # Use fetched price or default
        default_entry = st.session_state.get('live_entry_price', 250.0)
        default_exit = st.session_state.get('live_exit_price', 260.0)
        
        with col_price:
            entry_price = st.number_input("Entry Price", value=default_entry, key="entry_price")
        exit_price = st.number_input("Exit Price", value=default_exit, key="exit_price")
        quantity = st.number_input("Quantity", value=50, min_value=1, key="journal_qty")
        
        if st.button("📊 Generate Autopsy", key="gen_autopsy_btn"):
            with st.spinner("🔍 Capturing market context and generating autopsy..."):
                try:
                    # Create trade execution
                    intent = TradeIntent(
                        action="buy",
                        symbol=symbol,
                        quantity=quantity,
                        order_type="market",
                        price=entry_price,
                        timestamp=datetime.now(),
                        natural_language_prompt=f"Test trade for {symbol}"
                    )
                    
                    trade = TradeExecution(
                        trade_id=f"demo_{int(time.time())}",
                        intent=intent,
                        sentinel_check=SentinelResult(
                            approved=True,
                            inference_time_ms=5.0,
                            violated_rules=[],
                            risk_score=0.3,
                            reasoning="Demo trade",
                            recommended_action="allow"
                        ),
                        execution_timestamp=datetime.now(),
                        status="executed",
                        actual_fill_price=entry_price
                    )
                    
                    # Capture context
                    context = st.session_state.journal.capture_context(trade)
                    st.session_state.trade_context = context
                    
                    # Generate autopsy
                    autopsy = st.session_state.journal.generate_autopsy(
                        trade,
                        context,
                        f"Exit at ${exit_price}"
                    )
                    st.session_state.autopsy = autopsy
                    
                    st.success("✅ Autopsy generated!")
                except Exception as e:
                    st.error(f"❌ Autopsy failed: {e}")
    
    with col2:
        st.markdown("#### Trade Autopsy")
        
        if 'autopsy' in st.session_state:
            autopsy = st.session_state.autopsy
            context = st.session_state.trade_context
            
            # Show context
            st.markdown("**Market Context:**")
            st.json({
                "Symbol": context.symbol,
                "Current Price": f"${context.current_price:.2f}",
                "RSI": f"{context.rsi:.2f}" if context.rsi else "N/A",
                "News Articles": len(context.news_headlines),
                "Sentiment": f"{context.sentiment_score:.2f}" if context.sentiment_score else "N/A"
            })
            
            # Show autopsy
            with st.expander("📋 Full Autopsy Report", expanded=True):
                st.markdown(autopsy[:1500] + "..." if len(autopsy) > 1500 else autopsy)

def render_intelligence_demo():
    """FR4: Retail Intelligence Layer Demo"""
    st.markdown("### 🌐 FR4: Retail Intelligence Layer (Multi-Agent Swarm)")
    
    col_input, col_examples = st.columns([2, 1])
    with col_input:
        symbol = st.text_input("Symbol to analyze", "NVDA", key="intel_symbol")
    with col_examples:
        st.caption("Try: AAPL, TSLA, MSFT, GOOGL, AMZN")
    
    if st.button("🔍 Gather Intelligence", key="gather_intel_btn"):
        with st.spinner(f"🤖 Deploying 4 specialized agents for {symbol}..."):
            try:
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                report = loop.run_until_complete(
                    st.session_state.intelligence.gather_intelligence(symbol)
                )
                loop.close()
                
                st.session_state.intel_report = report
                st.success(f"✅ Intelligence gathered in {report['elapsed_seconds']:.2f}s")
            except Exception as e:
                st.error(f"❌ Intelligence gathering failed: {e}")
    
    if 'intel_report' in st.session_state:
        report = st.session_state.intel_report
        
        # Agent status
        st.markdown("#### Agent Status")
        col1, col2, col3, col4 = st.columns(4)
        
        raw_intel = report.get('raw_intelligence', [])
        agent_data = {intel.get('source'): intel for intel in raw_intel}
        
        agents = ["NewsAgent", "SentimentAgent", "TechnicalAgent", "VolatilityAgent"]
        cols = [col1, col2, col3, col4]
        
        for agent, col in zip(agents, cols):
            with col:
                has_error = agent_data.get(agent, {}).get('error')
                if has_error:
                    st.markdown(f'<span class="agent-status" style="background: rgba(255,100,100,0.3);">⚠ {agent}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="agent-status agent-active">✓ {agent}</span>', unsafe_allow_html=True)
        
        # Synthesis
        st.markdown("#### Intelligence Synthesis")
        synthesis = report.get('synthesis', {})
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Risk Score", f"{synthesis.get('risk_score', 0)}/10")
        col_b.metric("Confidence", f"{synthesis.get('confidence', 0)}%")
        col_c.metric("Agents", f"{report.get('agent_count', 0)}/4")
        
        # Key signals
        st.markdown("**Key Signals:**")
        for signal in synthesis.get('key_signals', [])[:3]:
            st.markdown(f"- {signal}")
        
        # Institutional edge
        st.info(f"**💡 Institutional Edge:** {synthesis.get('institutional_edge', 'N/A')}")
        
        # Actions
        st.markdown("**Recommended Actions:**")
        for action in synthesis.get('recommended_actions', []):
            st.markdown(f"- {action}")
        
        # Raw agent data expander
        with st.expander("📊 View Raw Agent Data"):
            for intel in raw_intel:
                source = intel.get('source', 'Unknown')
                st.markdown(f"**{source}:**")
                
                if source == "TechnicalAgent":
                    indicators = intel.get('indicators', {})
                    if intel.get('current_price'):
                        st.markdown(f"- Current Price: **${intel.get('current_price', 0):.2f}** ({intel.get('price_change_pct', 0):+.2f}%)")
                    st.markdown(f"- RSI: {indicators.get('rsi', 0):.1f}")
                    st.markdown(f"- MACD: {indicators.get('macd', 0):.3f} (Signal: {indicators.get('macd_signal', 0):.3f})")
                    signals = intel.get('signals', [])
                    for sig in signals[:3]:
                        st.markdown(f"  - {sig}")
                        
                elif source == "VolatilityAgent":
                    vol = intel.get('volatility', {})
                    st.markdown(f"- Historical Vol: {vol.get('historical_annual', 0):.1f}%")
                    st.markdown(f"- Recent Vol (20d): {vol.get('recent_20d', 0):.1f}%")
                    st.markdown(f"- ATR%: {vol.get('atr_pct', 0):.2f}%")
                    st.markdown(f"- Beta: {vol.get('beta', 1.0):.2f}")
                    st.markdown(f"- Regime: **{intel.get('regime', 'N/A')}** | Risk: **{intel.get('risk_level', 'N/A')}**")
                    
                elif source == "SentimentAgent":
                    st.markdown(f"- Sentiment: **{intel.get('overall_sentiment', 'N/A')}**")
                    st.markdown(f"- Score: {intel.get('sentiment_score', 0):.2f}")
                    themes = intel.get('key_themes', [])
                    if themes:
                        st.markdown(f"- Themes: {', '.join(themes[:3])}")
                        
                elif source == "NewsAgent":
                    headlines = intel.get('headlines', [])
                    if headlines:
                        for h in headlines[:3]:
                            if isinstance(h, dict):
                                st.markdown(f"  - {h.get('title', 'N/A')}")
                            else:
                                st.markdown(f"  - {h}")
                    else:
                        st.markdown("  - No news available")
                
                st.markdown("---")

def main():
    """Main dashboard"""
    # Add animated background elements
    st.markdown('''
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden;">
        <div style="position: absolute; width: 300px; height: 300px; border-radius: 50%; background: radial-gradient(circle, rgba(79, 172, 254, 0.15) 0%, transparent 70%); top: 10%; left: 10%; animation: float 15s ease-in-out infinite;"></div>
        <div style="position: absolute; width: 400px; height: 400px; border-radius: 50%; background: radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, transparent 70%); bottom: 15%; right: 15%; animation: float 20s ease-in-out infinite reverse;"></div>
        <div style="position: absolute; width: 250px; height: 250px; border-radius: 50%; background: radial-gradient(circle, rgba(0, 242, 254, 0.1) 0%, transparent 70%); top: 50%; right: 20%; animation: float 18s ease-in-out infinite;"></div>
    </div>
    ''', unsafe_allow_html=True)
    
    render_header()
    
    # Initialize engines
    if not st.session_state.initialized:
        with st.spinner("🚀 Initializing Agentic Brokerage OS..."):
            if not init_engines():
                st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">', unsafe_allow_html=True)
        st.markdown('<h2 style="background: linear-gradient(135deg, #4facfe 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 1.5rem;">🎯 Features</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        feature = st.radio(
            "Select Feature to Demo:",
            [
                "🛡️ Pre-Trade Sentinel",
                "🧠 Strategy Engine",
                "📝 RAG Journaling",
                "🌐 Intelligence Layer"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown('<div style="margin: 2rem 0; height: 2px; background: linear-gradient(90deg, transparent, rgba(79, 172, 254, 0.5), transparent); border-radius: 2px;"></div>', unsafe_allow_html=True)
        
        st.markdown("### System Info")
        st.markdown(f"**Groq API:** {'✓ Configured' if st.session_state.groq_key else '✗ Missing'}")
        st.markdown(f"**News API:** {'✓ Configured' if st.session_state.news_key else '✗ Optional'}")
        st.markdown(f"**Engines:** {4 if st.session_state.initialized else 0}/4 Active")
    
    # Main content
    st.markdown('<div style="margin: 3rem 0 2rem 0; height: 2px; background: linear-gradient(90deg, transparent, rgba(79, 172, 254, 0.5), rgba(168, 85, 247, 0.5), transparent); border-radius: 2px;"></div>', unsafe_allow_html=True)
    
    if feature == "🛡️ Pre-Trade Sentinel":
        render_sentinel_demo()
    elif feature == "🧠 Strategy Engine":
        render_strategy_demo()
    elif feature == "📝 RAG Journaling":
        render_journal_demo()
    elif feature == "🌐 Intelligence Layer":
        render_intelligence_demo()
    
    # Footer
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: rgba(226, 232, 240, 0.5); font-size: 0.95rem; margin-top: 2rem;">Built with ❤️ using Groq, LangGraph, and Streamlit | Hackathon 2026</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
