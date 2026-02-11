"""Core modules for the Agentic Brokerage OS"""

from .state import *

# Lazy import for PerceptionEngine - only available on desktop with GUI
# Import it directly when needed: from src.core.perception import PerceptionEngine

def get_perception_engine():
    """Get PerceptionEngine class. Only available on desktop with GUI."""
    from .perception import PerceptionEngine
    return PerceptionEngine

# Note: Orchestrator uses PerceptionEngine, so it's also desktop-only
# For API/headless usage, import engines directly instead

__all__ = ["get_perception_engine"]
