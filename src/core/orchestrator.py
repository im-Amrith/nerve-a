"""
LangGraph Orchestrator: Multi-agent workflow for Perception-Reasoning-Action loop.
Coordinates between specialized agents to handle trading decisions.
"""

from typing import Dict, List, TypedDict
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from loguru import logger

from .state import (
    AgentState, 
    TradeIntent, 
    TradeExecution,
    UserConstitution,
    PerceptionResult
)
from .perception import PerceptionEngine
from ..engines.pre_trade_sentinel import PreTradeSentinel
from ..engines.strategy_engine import StrategyEngine
from ..engines.rag_journal import RAGJournal


class Orchestrator:
    """
    Main orchestration layer using LangGraph to manage the PRA loop:
    Perception → Reasoning → Sentinel → Action → Journaling
    """
    
    def __init__(
        self,
        groq_api_key: str,
        user_constitution: UserConstitution,
        news_api_key: str = None,
        vector_db_client = None
    ):
        # Initialize all engines
        self.perception_engine = PerceptionEngine(groq_api_key)
        self.sentinel = PreTradeSentinel(groq_api_key, user_constitution)
        self.strategy_engine = StrategyEngine(groq_api_key)
        self.journal = RAGJournal(groq_api_key, news_api_key, vector_db_client)
        
        self.session_id = str(uuid.uuid4())
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """
        Build the stateful workflow graph:
        
        START → Perceive → Reason → Sentinel → Act → Journal → END
                    ↓                              ↓
                 [UI Changed?] ---------------→ [Blocked?]
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes (agent functions)
        workflow.add_node("perceive", self.perceive_node)
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("sentinel", self.sentinel_node)
        workflow.add_node("act", self.act_node)
        workflow.add_node("journal", self.journal_node)
        
        # Define edges (flow control)
        workflow.set_entry_point("perceive")
        
        workflow.add_edge("perceive", "reason")
        workflow.add_edge("reason", "sentinel")
        
        # Conditional: if sentinel approves, act; otherwise, skip to journal
        workflow.add_conditional_edges(
            "sentinel",
            self.should_execute_trade,
            {
                "execute": "act",
                "block": "journal"
            }
        )
        
        workflow.add_edge("act", "journal")
        workflow.add_edge("journal", END)
        
        return workflow.compile()
    
    def perceive_node(self, state: AgentState) -> AgentState:
        """
        Perception node: Capture and analyze UI state.
        """
        logger.info("🔍 PERCEIVE: Analyzing UI...")
        
        try:
            perception = self.perception_engine.perceive()
            
            state["current_perception"] = perception
            state["ui_change_detected"] = (
                state.get("last_ui_hash") != perception.ui_state_hash
            )
            state["last_ui_hash"] = perception.ui_state_hash
            
            if state["ui_change_detected"]:
                logger.warning("⚠️  UI change detected - adapting to new layout")
            
        except Exception as e:
            logger.error(f"Perception failed: {e}")
            state["error_state"] = f"Perception error: {e}"
        
        return state
    
    def reason_node(self, state: AgentState) -> AgentState:
        """
        Reasoning node: Parse user intent and create execution plan.
        """
        logger.info("🧠 REASON: Planning execution...")
        
        perception = state.get("current_perception")
        if not perception:
            state["error_state"] = "No perception data available"
            return state
        
        try:
            # Check if user input exists (could be from natural language or UI click)
            user_input = state.get("conversation_history", [])
            
            if user_input and len(user_input) > 0:
                last_input = user_input[-1].get("content", "")
                
                # Parse intent from natural language
                intent = self._parse_intent_from_nl(last_input, perception)
                state["user_intent"] = intent
                
                # Create execution plan
                plan = self._create_execution_plan(intent, perception)
                state["execution_plan"] = plan
                state["current_step"] = 0
            else:
                # No user input - just monitor UI
                state["next_action"] = "monitor"
            
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            state["error_state"] = f"Reasoning error: {e}"
        
        return state
    
    def sentinel_node(self, state: AgentState) -> AgentState:
        """
        Sentinel node: Safety checks and kill switch.
        """
        logger.info("🛡️  SENTINEL: Running safety checks...")
        
        intent = state.get("user_intent")
        if not intent:
            logger.info("No trade intent to check")
            return state
        
        try:
            # Get current portfolio (simplified - in production, fetch from broker API)
            portfolio = {
                "total_value": 100000,
                "cash": 50000,
                "positions": {},
                "current_prices": {intent.symbol: 100.0}
            }
            
            # Run sentinel checks
            result = self.sentinel.check_trade(intent, portfolio)
            state["sentinel_result"] = result
            
            if not result.approved:
                logger.warning(f"🚫 TRADE BLOCKED: {result.reasoning}")
                state["kill_switch_active"] = True
            else:
                logger.success(f"✅ Trade approved: {result.reasoning}")
                state["kill_switch_active"] = False
            
        except Exception as e:
            logger.error(f"Sentinel check failed: {e}")
            state["error_state"] = f"Sentinel error: {e}"
            state["kill_switch_active"] = True  # Fail-safe: block on error
        
        return state
    
    def act_node(self, state: AgentState) -> AgentState:
        """
        Action node: Execute approved trades.
        """
        logger.info("⚡ ACT: Executing trade...")
        
        intent = state.get("user_intent")
        perception = state.get("current_perception")
        
        if not intent or not perception:
            logger.error("Missing intent or perception data")
            return state
        
        try:
            # Execute the trade using coordinate mapping
            execution = self._execute_trade(intent, perception)
            
            state["executed_trades"].append(execution)
            
            # Update sentinel history
            self.sentinel.update_trade_history(execution)
            
            logger.success(f"✅ Trade executed: {execution.trade_id}")
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            state["error_state"] = f"Execution error: {e}"
        
        return state
    
    def journal_node(self, state: AgentState) -> AgentState:
        """
        Journaling node: Capture context and generate autopsy.
        """
        logger.info("📝 JOURNAL: Recording trade context...")
        
        executed_trades = state.get("executed_trades", [])
        
        if not executed_trades:
            logger.info("No trades to journal")
            return state
        
        try:
            latest_trade = executed_trades[-1]
            
            # Capture market context
            context = self.journal.capture_context(latest_trade)
            latest_trade.market_context = context.dict()
            
            # Generate autopsy
            autopsy = self.journal.generate_autopsy(latest_trade, context)
            
            logger.success(f"📊 Autopsy generated for {latest_trade.trade_id}")
            logger.info(f"\n{autopsy}\n")
            
        except Exception as e:
            logger.error(f"Journaling failed: {e}")
            state["error_state"] = f"Journal error: {e}"
        
        return state
    
    def should_execute_trade(self, state: AgentState) -> str:
        """Conditional edge: execute or block based on sentinel."""
        sentinel_result = state.get("sentinel_result")
        
        if sentinel_result and sentinel_result.approved:
            return "execute"
        else:
            return "block"
    
    def _parse_intent_from_nl(self, natural_language: str, perception: PerceptionResult) -> TradeIntent:
        """
        Parse natural language into TradeIntent.
        
        Examples:
        - "Buy 10 shares of AAPL"
        - "Sell 5 TSLA at market price"
        - "Place limit order for 100 shares of MSFT at $300"
        """
        from groq import Groq
        import json
        
        client = Groq(api_key=self.perception_engine.client.api_key)
        
        prompt = f"""Parse this trading instruction into structured JSON:

Instruction: "{natural_language}"

Return JSON with this exact format:
{{
  "action": "buy" or "sell",
  "symbol": "TICKER",
  "quantity": number,
  "order_type": "market" or "limit" or "stop",
  "price": number or null
}}

Respond ONLY with valid JSON."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100
        )
        
        raw = response.choices[0].message.content
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        
        parsed = json.loads(raw)
        
        return TradeIntent(
            action=parsed["action"],
            symbol=parsed["symbol"],
            quantity=parsed["quantity"],
            order_type=parsed["order_type"],
            price=parsed.get("price"),
            timestamp=datetime.now(),
            natural_language_prompt=natural_language
        )
    
    def _create_execution_plan(self, intent: TradeIntent, perception: PerceptionResult) -> List[str]:
        """Create step-by-step execution plan."""
        plan = []
        
        # Map intent to UI actions
        if intent.action == "buy":
            plan.append("Click 'Buy' button")
        elif intent.action == "sell":
            plan.append("Click 'Sell' button")
        
        plan.append(f"Enter quantity: {intent.quantity}")
        
        if intent.order_type == "limit" and intent.price:
            plan.append("Select 'Limit Order'")
            plan.append(f"Enter price: {intent.price}")
        elif intent.order_type == "market":
            plan.append("Select 'Market Order'")
        
        plan.append("Click 'Submit' button")
        
        return plan
    
    def _execute_trade(self, intent: TradeIntent, perception: PerceptionResult) -> TradeExecution:
        """
        Execute trade using coordinate mapping.
        In production, this would interact with actual broker API or UI automation.
        """
        trade = TradeExecution(
            trade_id=str(uuid.uuid4()),
            intent=intent,
            sentinel_check=None,  # Already checked
            execution_timestamp=datetime.now(),
            status="executed",  # Simulated success
            actual_fill_price=intent.price or 100.0  # Simulated fill
        )
        
        logger.info(f"Simulated trade execution: {intent.action} {intent.quantity} {intent.symbol}")
        
        return trade
    
    def run(self, user_input: str) -> Dict:
        """
        Main entry point: Process user input through the PRA loop.
        
        Args:
            user_input: Natural language trading instruction
            
        Returns:
            Final state after workflow completion
        """
        logger.info(f"Starting PRA loop for: '{user_input}'")
        
        # Initialize state
        initial_state: AgentState = {
            "current_perception": None,
            "ui_change_detected": False,
            "last_ui_hash": None,
            "user_intent": None,
            "execution_plan": [],
            "current_step": 0,
            "sentinel_result": None,
            "kill_switch_active": False,
            "user_constitution": self.sentinel.constitution.dict(),
            "active_strategies": list(self.strategy_engine.strategies.values()),
            "current_strategy": None,
            "pending_trades": [],
            "executed_trades": [],
            "conversation_history": [{"role": "user", "content": user_input}],
            "market_context": {},
            "rag_memories": [],
            "next_action": None,
            "error_state": None,
            "retry_count": 0,
            "session_id": self.session_id,
            "timestamp": datetime.now()
        }
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        logger.success("PRA loop completed")
        
        return final_state
    
    def run_strategy_generation(self, strategy_prompt: str) -> Dict:
        """
        Generate and backtest a strategy from natural language.
        
        Args:
            strategy_prompt: Natural language strategy description
            
        Returns:
            Strategy object with backtest results
        """
        logger.info(f"Generating strategy: '{strategy_prompt}'")
        
        strategy = self.strategy_engine.generate_strategy(strategy_prompt, auto_backtest=True)
        
        summary = self.strategy_engine.get_strategy_summary(strategy.strategy_id)
        logger.info(f"\n{summary}\n")
        
        return strategy.dict()
