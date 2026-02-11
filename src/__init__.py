"""Agentic Brokerage OS - Core Package"""

__version__ = "0.1.0"
__author__ = "Agentic Brokerage Team"

# State models are always safe to import
from .core.state import (
    AgentState,
    TradeIntent,
    UserConstitution,
    Strategy,
    TradeExecution,
    PerceptionResult
)

# Orchestrator requires desktop GUI (PerceptionEngine). Import directly when needed:
# from src.core.orchestrator import Orchestrator

def get_orchestrator():
    """Get Orchestrator class. Only available on desktop with GUI."""
    from .core.orchestrator import Orchestrator
    return Orchestrator

__all__ = [
    "get_orchestrator",
    "AgentState",
    "TradeIntent",
    "UserConstitution",
    "Strategy",
    "TradeExecution",
    "PerceptionResult"
]
