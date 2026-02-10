"""
Core state definitions for the Agentic Brokerage OS.
Defines the state structure passed between agents in the LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class UIElement(BaseModel):
    """Represents a detected UI element from visual perception."""
    
    element_type: str = Field(description="Type of UI element (button, input, chart, etc.)")
    coordinates: Dict[str, int] = Field(description="Bounding box {x, y, width, height}")
    confidence: float = Field(description="Detection confidence score 0-1")
    text_content: Optional[str] = Field(default=None, description="OCR extracted text")
    semantic_label: str = Field(description="Semantic meaning (e.g., 'buy_button', 'price_display')")


class PerceptionResult(BaseModel):
    """Output from the Perception Engine."""
    
    screenshot_timestamp: datetime
    detected_elements: List[UIElement]
    ui_state_hash: str = Field(description="Hash of current UI layout for change detection")
    raw_vision_response: str
    coordinate_map: Dict[str, Dict[str, int]] = Field(
        description="Map of semantic labels to coordinates"
    )


class TradeIntent(BaseModel):
    """User's trading intention parsed from natural language or UI interaction."""
    
    action: Literal["buy", "sell", "modify", "cancel"]
    symbol: str
    quantity: int
    order_type: Literal["market", "limit", "stop"]
    price: Optional[float] = None
    timestamp: datetime
    natural_language_prompt: Optional[str] = None


class SentinelResult(BaseModel):
    """Output from Pre-Trade Sentinel checks."""
    
    approved: bool
    inference_time_ms: float
    violated_rules: List[str] = Field(default_factory=list)
    risk_score: float = Field(ge=0, le=1, description="0=safe, 1=extreme risk")
    reasoning: str
    recommended_action: Literal["allow", "block", "modify", "delay"]


class Strategy(BaseModel):
    """Generated trading strategy from natural language."""
    
    strategy_id: str
    name: str
    description: str
    generated_code: str
    backtest_results: Optional[Dict[str, Any]] = None
    is_paper_trading: bool = True
    user_confirmed: bool = False
    created_at: datetime


class TradeExecution(BaseModel):
    """Record of an executed trade."""
    
    trade_id: str
    intent: TradeIntent
    sentinel_check: SentinelResult
    execution_timestamp: datetime
    status: Literal["pending", "executed", "failed", "blocked"]
    actual_fill_price: Optional[float] = None
    market_context: Optional[Dict[str, Any]] = None


class AgentState(TypedDict):
    """
    Main state object passed between agents in LangGraph.
    This represents the complete context at any point in the PRA loop.
    """
    
    # Perception
    current_perception: Optional[PerceptionResult]
    ui_change_detected: bool
    last_ui_hash: Optional[str]
    
    # Intent & Planning
    user_intent: Optional[TradeIntent]
    execution_plan: List[str]  # Step-by-step plan from reasoning engine
    current_step: int
    
    # Sentinel & Safety
    sentinel_result: Optional[SentinelResult]
    kill_switch_active: bool
    user_constitution: Dict[str, Any]  # Personalized trading rules
    
    # Strategy
    active_strategies: List[Strategy]
    current_strategy: Optional[Strategy]
    
    # Execution & History
    pending_trades: List[TradeExecution]
    executed_trades: List[TradeExecution]
    
    # Memory & Context
    conversation_history: List[Dict[str, str]]
    market_context: Dict[str, Any]
    rag_memories: List[str]  # Vector DB retrieval results
    
    # Control Flow
    next_action: Optional[str]
    error_state: Optional[str]
    retry_count: int
    
    # Metadata
    session_id: str
    timestamp: datetime


class UserConstitution(BaseModel):
    """
    User's personalized trading rules and guardrails.
    Acts as the rulebook for the Pre-Trade Sentinel.
    """
    
    # Position Limits
    max_position_size: float = Field(default=10000, description="Max $ per position")
    max_daily_loss: float = Field(default=5000, description="Daily loss limit")
    max_leverage: float = Field(default=1.5, description="Maximum leverage allowed")
    
    # Behavioral Guards
    min_time_between_trades: int = Field(default=60, description="Seconds between trades")
    max_trades_per_day: int = Field(default=10, description="Daily trade limit")
    block_after_loss_streak: int = Field(default=3, description="Block after N consecutive losses")
    
    # Emotional Filters
    block_on_tilt: bool = Field(default=True, description="Block trading after emotional indicators")
    require_cooldown: bool = Field(default=True, description="Mandatory cooldown after big loss")
    cooldown_duration_minutes: int = Field(default=30, description="Cooldown duration")
    
    # Asset Restrictions
    allowed_symbols: Optional[List[str]] = None
    blocked_symbols: Optional[List[str]] = None
    max_concentration: float = Field(default=0.3, description="Max % of portfolio in single asset")
    
    # Time-based Rules
    trading_hours_only: bool = Field(default=True, description="Block outside market hours")
    no_trade_zones: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        description="Time windows to block trading"
    )
    
    # Strategy Constraints
    strategies_require_backtest: bool = Field(default=True)
    min_backtest_trades: int = Field(default=30)
    min_sharpe_ratio: float = Field(default=1.0)
    
    # Kill Switch
    enable_kill_switch: bool = Field(default=True)
    kill_switch_conditions: List[Dict[str, Any]] = Field(default_factory=list)


class MarketContext(BaseModel):
    """
    Market context captured at trade execution time for RAG journaling.
    """
    
    timestamp: datetime
    symbol: str
    
    # Price Data
    current_price: float
    day_high: float
    day_low: float
    volume: int
    
    # Technical Indicators
    rsi: Optional[float] = None
    macd: Optional[Dict[str, float]] = None
    moving_averages: Optional[Dict[str, float]] = None
    
    # Sentiment & News
    news_headlines: List[str] = Field(default_factory=list)
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    social_mentions: Optional[int] = None
    
    # Market Conditions
    market_regime: Optional[Literal["trending", "ranging", "volatile"]] = None
    correlation_to_index: Optional[float] = None
    sector_performance: Optional[float] = None
