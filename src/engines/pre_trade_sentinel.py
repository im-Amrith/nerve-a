"""
Pre-Trade Sentinel (FR1): Real-time safety checks and kill switch.
Intercepts orders between client and exchange API with <50ms latency requirement.
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from groq import Groq
from loguru import logger
from pydantic import BaseModel

from ..core.state import TradeIntent, SentinelResult, UserConstitution, TradeExecution


class PreTradeSentinel:
    """
    Acts as a hard kill switch for trades that violate user constitution.
    Must complete analysis in <50ms to meet latency requirements.
    """
    
    def __init__(self, groq_api_key: str, user_constitution: UserConstitution):
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.1-8b-instant"  # Fast model for low latency
        self.constitution = user_constitution
        self.trade_history: List[TradeExecution] = []
        self.last_trade_time: Optional[datetime] = None
        self.consecutive_losses = 0
        self.cooldown_until: Optional[datetime] = None
        
    def check_trade(self, intent: TradeIntent, current_portfolio: Dict) -> SentinelResult:
        """
        Main entry point: run all safety checks on a trade intent.
        
        Args:
            intent: The proposed trade
            current_portfolio: Current positions and cash balance
            
        Returns:
            SentinelResult with approval/denial and reasoning
        """
        start_time = time.time()
        violated_rules = []
        risk_score = 0.0
        
        logger.info(f"Sentinel checking: {intent.action} {intent.quantity} {intent.symbol}")
        
        # Fast deterministic checks first (microseconds)
        violated_rules.extend(self._check_position_limits(intent, current_portfolio))
        violated_rules.extend(self._check_timing_rules(intent))
        violated_rules.extend(self._check_asset_restrictions(intent))
        violated_rules.extend(self._check_behavioral_guards(intent))
        violated_rules.extend(self._check_cooldown())
        
        # Compute basic risk score
        risk_score = self._compute_risk_score(intent, current_portfolio, violated_rules)
        
        # LLM-based reasoning (only if needed for edge cases)
        llm_reasoning = None
        if 0.3 < risk_score < 0.7:  # Only invoke LLM for borderline cases
            llm_reasoning = self._llm_risk_assessment(intent, violated_rules)
            if llm_reasoning.get("additional_risks"):
                violated_rules.extend(llm_reasoning["additional_risks"])
                risk_score = max(risk_score, llm_reasoning.get("adjusted_risk_score", risk_score))
        
        # Determine final decision
        if self.constitution.enable_kill_switch and violated_rules:
            approved = False
            recommended_action = "block"
            reasoning = f"BLOCKED: {len(violated_rules)} rule violations: {', '.join(violated_rules[:3])}"
        elif risk_score > 0.8:
            approved = False
            recommended_action = "block"
            reasoning = f"BLOCKED: Risk score {risk_score:.2f} exceeds threshold"
        elif risk_score > 0.5:
            approved = True
            recommended_action = "delay"
            reasoning = f"CAUTION: Moderate risk ({risk_score:.2f}), suggest review"
        else:
            approved = True
            recommended_action = "allow"
            reasoning = f"APPROVED: Low risk ({risk_score:.2f}), all checks passed"
        
        inference_time_ms = (time.time() - start_time) * 1000
        
        if inference_time_ms > 50:
            logger.warning(f"Sentinel exceeded latency target: {inference_time_ms:.2f}ms > 50ms")
        else:
            logger.success(f"Sentinel check complete in {inference_time_ms:.2f}ms")
        
        return SentinelResult(
            approved=approved,
            inference_time_ms=inference_time_ms,
            violated_rules=violated_rules,
            risk_score=risk_score,
            reasoning=reasoning,
            recommended_action=recommended_action
        )
    
    def _check_position_limits(self, intent: TradeIntent, portfolio: Dict) -> List[str]:
        """Check position size and leverage limits."""
        violations = []
        
        # Estimate position value
        estimated_price = intent.price or portfolio.get("current_prices", {}).get(intent.symbol, 100)
        position_value = intent.quantity * estimated_price
        
        if position_value > self.constitution.max_position_size:
            violations.append(
                f"Position size ${position_value:.2f} exceeds limit ${self.constitution.max_position_size}"
            )
        
        # Check total portfolio value and leverage
        total_value = portfolio.get("total_value", 0)
        if total_value > 0:
            leverage = position_value / total_value
            if leverage > self.constitution.max_leverage:
                violations.append(
                    f"Leverage {leverage:.2f}x exceeds limit {self.constitution.max_leverage}x"
                )
        
        # Check concentration
        if total_value > 0:
            concentration = position_value / total_value
            if concentration > self.constitution.max_concentration:
                violations.append(
                    f"Concentration {concentration:.1%} exceeds limit {self.constitution.max_concentration:.1%}"
                )
        
        return violations
    
    def _check_timing_rules(self, intent: TradeIntent) -> List[str]:
        """Check time-based trading rules."""
        violations = []
        
        # Check minimum time between trades
        if self.last_trade_time:
            time_since_last = (intent.timestamp - self.last_trade_time).total_seconds()
            if time_since_last < self.constitution.min_time_between_trades:
                violations.append(
                    f"Only {time_since_last:.1f}s since last trade (min: {self.constitution.min_time_between_trades}s)"
                )
        
        # Check daily trade limit
        today_trades = [
            t for t in self.trade_history
            if t.execution_timestamp.date() == intent.timestamp.date()
        ]
        if len(today_trades) >= self.constitution.max_trades_per_day:
            violations.append(
                f"Daily trade limit reached ({len(today_trades)}/{self.constitution.max_trades_per_day})"
            )
        
        # Check trading hours
        if self.constitution.trading_hours_only:
            hour = intent.timestamp.hour
            # Market hours 9:30 AM - 4:00 PM ET (simplified)
            if not (9 <= hour < 16):
                violations.append(f"Outside trading hours (current: {hour}:00)")
        
        return violations
    
    def _check_asset_restrictions(self, intent: TradeIntent) -> List[str]:
        """Check symbol whitelist/blacklist."""
        violations = []
        
        if self.constitution.allowed_symbols:
            if intent.symbol not in self.constitution.allowed_symbols:
                violations.append(f"Symbol {intent.symbol} not in allowed list")
        
        if self.constitution.blocked_symbols:
            if intent.symbol in self.constitution.blocked_symbols:
                violations.append(f"Symbol {intent.symbol} is blocked")
        
        return violations
    
    def _check_behavioral_guards(self, intent: TradeIntent) -> List[str]:
        """Check for tilt/emotional trading indicators."""
        violations = []
        
        # Check loss streaks
        recent_trades = self.trade_history[-10:] if self.trade_history else []
        consecutive_losses = 0
        for trade in reversed(recent_trades):
            if trade.status == "executed" and trade.actual_fill_price:
                # Simplified P&L check
                is_loss = (
                    (trade.intent.action == "sell" and trade.actual_fill_price < (trade.intent.price or 0))
                    or (trade.intent.action == "buy" and trade.actual_fill_price > (trade.intent.price or 0))
                )
                if is_loss:
                    consecutive_losses += 1
                else:
                    break
        
        if consecutive_losses >= self.constitution.block_after_loss_streak:
            violations.append(
                f"Blocked due to {consecutive_losses} consecutive losses (tilt protection)"
            )
        
        return violations
    
    def _check_cooldown(self) -> List[str]:
        """Check if user is in mandatory cooldown period."""
        violations = []
        
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            remaining = (self.cooldown_until - datetime.now()).total_seconds() / 60
            violations.append(f"In cooldown period ({remaining:.1f} minutes remaining)")
        
        return violations
    
    def _compute_risk_score(
        self, 
        intent: TradeIntent, 
        portfolio: Dict,
        violations: List[str]
    ) -> float:
        """
        Compute normalized risk score 0-1.
        
        Factors:
        - Number of rule violations
        - Position size relative to portfolio
        - Recent loss streak
        - Order type (market orders higher risk)
        """
        score = 0.0
        
        # Violations contribute heavily
        score += len(violations) * 0.2
        
        # Position size risk
        total_value = portfolio.get("total_value", 1)
        estimated_price = intent.price or 100
        position_value = intent.quantity * estimated_price
        size_ratio = position_value / total_value if total_value > 0 else 0
        score += min(size_ratio, 1.0) * 0.3
        
        # Market orders are riskier
        if intent.order_type == "market":
            score += 0.1
        
        # Loss streak risk
        score += min(self.consecutive_losses * 0.15, 0.4)
        
        return min(score, 1.0)
    
    def _llm_risk_assessment(self, intent: TradeIntent, violations: List[str]) -> Dict:
        """
        Use LLM for nuanced risk assessment (only for borderline cases).
        Kept minimal to maintain <50ms latency budget.
        """
        try:
            prompt = f"""You are a trading risk analyst. Assess this trade quickly:

Trade: {intent.action.upper()} {intent.quantity} {intent.symbol} @ {intent.order_type}
Known violations: {violations if violations else "None"}

Respond with JSON only:
{{
  "additional_risks": ["risk1", "risk2"],
  "adjusted_risk_score": 0.0-1.0,
  "brief_reasoning": "one sentence"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=150,
                timeout=5.0  # 5 second timeout
            )
            
            import json
            raw = response.choices[0].message.content
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            return json.loads(raw)
        except Exception as e:
            logger.error(f"LLM risk assessment failed: {e}")
            return {"additional_risks": [], "adjusted_risk_score": 0.5}
    
    def trigger_cooldown(self, duration_minutes: Optional[int] = None):
        """Manually trigger cooldown period (e.g., after large loss)."""
        duration = duration_minutes or self.constitution.cooldown_duration_minutes
        self.cooldown_until = datetime.now() + timedelta(minutes=duration)
        logger.warning(f"Cooldown activated for {duration} minutes until {self.cooldown_until}")
    
    def update_trade_history(self, trade: TradeExecution):
        """Update internal history for behavioral tracking."""
        self.trade_history.append(trade)
        self.last_trade_time = trade.execution_timestamp
        
        # Update loss streak
        if trade.status == "executed" and trade.actual_fill_price:
            # Simplified loss detection
            intent_price = trade.intent.price or trade.actual_fill_price
            is_loss = abs(trade.actual_fill_price - intent_price) > intent_price * 0.02
            
            if is_loss:
                self.consecutive_losses += 1
            else:
                self.consecutive_losses = 0
        
        # Auto-trigger cooldown on loss streak
        if self.constitution.require_cooldown and self.consecutive_losses >= 3:
            self.trigger_cooldown()
