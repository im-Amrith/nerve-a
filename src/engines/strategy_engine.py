"""
Semantic Strategy Engine (FR2): Natural language to executable trading algorithms.
Converts prompts like "Buy if RSI > 60" into backtested Python strategies.
"""

import ast
import time
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from groq import Groq
from loguru import logger

from ..core.state import Strategy


class StrategyEngine:
    """
    Converts natural language trading ideas into executable, backtested strategies.
    Enforces safety defaults: paper trading first, explicit user confirmation for live.
    """
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"  # Better for code generation
        self.strategies: Dict[str, Strategy] = {}
        
    def generate_strategy(
        self, 
        natural_language_prompt: str,
        auto_backtest: bool = True,
        **kwargs
    ) -> Strategy:
        """
        Convert natural language to executable trading strategy.
        
        Args:
            natural_language_prompt: User's trading idea
            auto_backtest: Whether to automatically run backtest
            backtest_symbol: Stock symbol for backtesting (default: SPY)
            
        Returns:
            Strategy object with generated code and backtest results
        """
        logger.info(f"Generating strategy from: '{natural_language_prompt}'")
        
        # Generate code using LLM
        generated_code = self._generate_code(natural_language_prompt)
        
        # Validate and sanitize code
        validated_code = self._validate_code(generated_code)
        
        # Create strategy object
        strategy = Strategy(
            strategy_id=str(uuid.uuid4()),
            name=self._extract_strategy_name(natural_language_prompt),
            description=natural_language_prompt,
            generated_code=validated_code,
            backtest_results=None,
            is_paper_trading=True,  # Always default to paper trading
            user_confirmed=False,
            created_at=datetime.now()
        )
        
        # Auto-backtest if requested
        if auto_backtest:
            symbol = kwargs.get('backtest_symbol', 'SPY')
            strategy.backtest_results = self.backtest_strategy(strategy, symbol=symbol)
        
        self.strategies[strategy.strategy_id] = strategy
        logger.success(f"Strategy generated: {strategy.name} ({strategy.strategy_id})")
        
        return strategy
    
    def _generate_code(self, prompt: str) -> str:
        """Use LLM to generate Python trading strategy code."""
        
        system_prompt = """You are an expert quantitative trading strategy developer. 
Generate PRODUCTION-READY Python code for trading strategies based on user prompts.

AVAILABLE DATA COLUMNS (pre-computed in the DataFrame):
- OHLCV: 'open', 'high', 'low', 'close', 'volume', 'date'
- Moving Averages: 'sma_10', 'sma_20', 'sma_50', 'sma_200'
- RSI (14): 'rsi' (0-100 scale)
- MACD: 'macd', 'macd_signal', 'macd_histogram'
- Bollinger Bands: 'bb_upper', 'bb_middle', 'bb_lower'
- ATR (14): 'atr'
- Volume: 'volume_sma', 'volume_ratio'

CRITICAL REQUIREMENTS:
1. Use pandas for data manipulation
2. Generate ACTUAL trading signals - DO NOT return all zeros
3. Implement a Strategy class with these methods:
   - __init__(self, params: dict) 
   - generate_signals(self, data: pd.DataFrame) -> pd.Series
   - calculate_position_size(self, price: float, capital: float) -> int
4. The generate_signals method MUST:
   - Return pd.Series with values: 1 (long), -1 (short), 0 (no position)
   - Use the EXACT column names listed above
   - Generate both entry and exit signals based on the strategy logic
5. Include proper error handling and parameter validation

WORKING EXAMPLE for RSI + MACD strategy:
import pandas as pd
import numpy as np
from typing import Dict

class Strategy:
    \"\"\"
    Trading strategy based on RSI and MACD indicators.
    
    Parameters:
    params (dict): Strategy parameters.
        - rsi_period (int): RSI calculation period.
        - macd_fast_period (int): MACD fast EMA period.
        - macd_slow_period (int): MACD slow EMA period.
        - macd_signal_period (int): MACD signal EMA period.
        - max_position_pct (float): Maximum position size as a percentage of capital.
    \"\"\"
    
    def __init__(self, params: Dict = None):
        \"\"\"Initialize the strategy with parameters.\"\"\"
        self.params = params or {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'max_position_pct': 0.1
        }
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        \"\"\"
        Generate buy/sell signals based on RSI and MACD.
        
        Args:
            data: DataFrame with OHLCV and indicator columns
            
        Returns:
            Series with 1 (buy), -1 (sell), 0 (hold)
        \"\"\"
        signals = pd.Series(0, index=data.index)
        
        # Get parameters
        rsi_oversold = self.params.get('rsi_oversold', 30)
        rsi_overbought = self.params.get('rsi_overbought', 70)
        
        # MACD crossover signals
        macd_cross_up = (data['macd'] > data['macd_signal']) & (data['macd'].shift(1) <= data['macd_signal'].shift(1))
        macd_cross_down = (data['macd'] < data['macd_signal']) & (data['macd'].shift(1) >= data['macd_signal'].shift(1))
        
        # Buy when RSI oversold AND MACD crosses above signal
        buy_condition = (data['rsi'] < rsi_oversold) | macd_cross_up
        signals[buy_condition] = 1
        
        # Sell when RSI overbought OR MACD crosses below signal
        sell_condition = (data['rsi'] > rsi_overbought) | macd_cross_down
        signals[sell_condition] = -1
        
        return signals
    
    def calculate_position_size(self, price: float, capital: float) -> int:
        \"\"\"Calculate position size based on risk management.\"\"\"
        max_position_value = capital * self.params.get('max_position_pct', 0.1)
        quantity = int(max_position_value / price)
        return max(1, quantity)

Return ONLY executable Python code. No markdown formatting or explanations."""

        user_prompt = f"""Generate a trading strategy for this requirement:

"{prompt}"

Use the pre-computed indicator columns. Ensure generate_signals returns actual 1/-1/0 signals."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            code = response.choices[0].message.content
            
            # Extract code from markdown if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            
            return code
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise
    
    def _validate_code(self, code: str) -> str:
        """
        Validate and sanitize generated code for safety.
        
        Checks:
        - Valid Python syntax
        - No dangerous imports (os, subprocess, etc.)
        - Has required Strategy class and methods
        """
        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Generated code has syntax errors: {e}")
            raise ValueError(f"Invalid Python syntax: {e}")
        
        # Check for dangerous imports
        dangerous_imports = ['os', 'subprocess', 'sys', 'eval', 'exec', '__import__']
        for dangerous in dangerous_imports:
            if f"import {dangerous}" in code or f"from {dangerous}" in code:
                logger.error(f"Code contains dangerous import: {dangerous}")
                raise ValueError(f"Security violation: {dangerous} import not allowed")
        
        # Verify required class exists
        if "class Strategy" not in code:
            logger.error("Generated code missing Strategy class")
            raise ValueError("Code must define a Strategy class")
        
        # Verify required methods
        required_methods = ["generate_signals", "calculate_position_size"]
        for method in required_methods:
            if f"def {method}" not in code:
                logger.warning(f"Code missing recommended method: {method}")
        
        logger.success("Code validation passed")
        return code
    
    def backtest_strategy(
        self, 
        strategy: Strategy,
        historical_data: Optional[pd.DataFrame] = None,
        symbol: str = "SPY"
    ) -> Dict:
        """
        Run historical backtest on strategy.
        
        Args:
            strategy: Strategy to backtest
            historical_data: OHLCV data (if None, fetches real data or generates synthetic)
            symbol: Stock symbol to fetch data for (default: SPY)
            
        Returns:
            Backtest results with P&L, Sharpe ratio, max drawdown, etc.
        """
        logger.info(f"Backtesting strategy: {strategy.name}")
        
        # Try to fetch real data, fallback to synthetic
        if historical_data is None:
            historical_data = self._fetch_historical_data(symbol)
            if historical_data is None or historical_data.empty:
                logger.warning(f"Could not fetch real data for {symbol}, using synthetic data")
                historical_data = self._generate_synthetic_data()
        
        try:
            # Execute strategy code in isolated namespace
            namespace = {'pd': pd, 'np': np}  # Provide common imports
            exec(strategy.generated_code, namespace)
            
            # Instantiate strategy with default params
            StrategyClass = namespace.get('Strategy')
            if not StrategyClass:
                raise ValueError("Strategy class not found in generated code")
            
            # Try with params, fallback to no params
            try:
                strategy_instance = StrategyClass(params={})
            except TypeError:
                strategy_instance = StrategyClass()
            
            # Generate signals
            signals = strategy_instance.generate_signals(historical_data)
            
            # Calculate returns
            results = self._calculate_backtest_metrics(historical_data, signals)
            
            logger.success(f"Backtest complete: PnL={results['total_return']:.2%}, Sharpe={results['sharpe_ratio']:.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Backtest execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
    
    def _fetch_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetch real historical data from Yahoo Finance."""
        try:
            import yfinance as yf
            
            logger.info(f"Fetching historical data for {symbol}...")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Rename columns to lowercase
            data.columns = [c.lower() for c in data.columns]
            data = data.reset_index()
            data.columns = [c.lower() if isinstance(c, str) else c for c in data.columns]
            
            # Rename 'date' column if needed
            if 'datetime' in data.columns:
                data = data.rename(columns={'datetime': 'date'})
            
            # Add technical indicators
            data = self._add_indicators(data)
            
            logger.success(f"Fetched {len(data)} days of data for {symbol}")
            return data.dropna()
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return None
    
    def _add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to OHLCV data."""
        # Moving Averages
        data['sma_10'] = data['close'].rolling(10).mean()
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['sma_200'] = data['close'].rolling(200).mean()
        
        # RSI (14-period)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (12, 26, 9)
        ema_12 = data['close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['close'].ewm(span=26, adjust=False).mean()
        data['macd'] = ema_12 - ema_26
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # Bollinger Bands (20-period, 2 std)
        data['bb_middle'] = data['close'].rolling(20).mean()
        data['bb_std'] = data['close'].rolling(20).std()
        data['bb_upper'] = data['bb_middle'] + (data['bb_std'] * 2)
        data['bb_lower'] = data['bb_middle'] - (data['bb_std'] * 2)
        
        # Average True Range (ATR)
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data['atr'] = true_range.rolling(14).mean()
        
        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        return data
    
    def _generate_synthetic_data(self, days: int = 252) -> pd.DataFrame:
        """Generate synthetic OHLCV data for backtesting."""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Geometric Brownian Motion for price simulation
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, days)
        price = 100 * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'date': dates,
            'open': price * np.random.uniform(0.98, 1.02, days),
            'high': price * np.random.uniform(1.00, 1.05, days),
            'low': price * np.random.uniform(0.95, 1.00, days),
            'close': price,
            'volume': np.random.randint(1000000, 10000000, days)
        })
        
        # Add technical indicators
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['sma_10'] = data['close'].rolling(10).mean()
        data['sma_200'] = data['close'].rolling(200).mean()
        
        # RSI (14-period)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (12, 26, 9)
        ema_12 = data['close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['close'].ewm(span=26, adjust=False).mean()
        data['macd'] = ema_12 - ema_26
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # Bollinger Bands (20-period, 2 std)
        data['bb_middle'] = data['close'].rolling(20).mean()
        data['bb_std'] = data['close'].rolling(20).std()
        data['bb_upper'] = data['bb_middle'] + (data['bb_std'] * 2)
        data['bb_lower'] = data['bb_middle'] - (data['bb_std'] * 2)
        
        # Average True Range (ATR)
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data['atr'] = true_range.rolling(14).mean()
        
        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        return data.dropna()
    
    def _calculate_backtest_metrics(
        self, 
        data: pd.DataFrame, 
        signals: pd.Series
    ) -> Dict:
        """Calculate backtest performance metrics."""
        
        # Align signals with data
        data = data.copy()
        data['signal'] = signals
        data['returns'] = data['close'].pct_change()
        data['strategy_returns'] = data['signal'].shift(1) * data['returns']
        
        # Drop NaN values
        data = data.dropna()
        
        # Calculate metrics
        total_return = (1 + data['strategy_returns']).prod() - 1
        
        # Sharpe ratio (annualized)
        sharpe_ratio = (
            data['strategy_returns'].mean() / data['strategy_returns'].std() * np.sqrt(252)
            if data['strategy_returns'].std() > 0 else 0
        )
        
        # Maximum drawdown
        cumulative = (1 + data['strategy_returns']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        winning_trades = (data['strategy_returns'] > 0).sum()
        total_trades = (data['signal'] != 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            "status": "success",
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate),
            "total_trades": int(total_trades),
            "winning_trades": int(winning_trades),
            "backtest_period_days": len(data),
            "final_portfolio_value": float((1 + data['strategy_returns']).prod() * 10000)
        }
    
    def _extract_strategy_name(self, prompt: str) -> str:
        """Extract a concise strategy name from the prompt."""
        # Simple heuristic: first 5 words
        words = prompt.split()[:5]
        name = "_".join(words).lower()
        name = "".join(c for c in name if c.isalnum() or c == "_")
        return name[:50]
    
    def approve_for_live_trading(self, strategy_id: str) -> bool:
        """
        User confirmation required to move strategy from paper to live trading.
        
        Args:
            strategy_id: Strategy to approve
            
        Returns:
            True if approved and meets minimum requirements
        """
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            logger.error(f"Strategy {strategy_id} not found")
            return False
        
        # Check backtest requirements
        if not strategy.backtest_results:
            logger.error("Strategy must be backtested before live approval")
            return False
        
        results = strategy.backtest_results
        
        # Minimum requirements for live trading
        min_trades = 30
        min_sharpe = 1.0
        
        if results.get("total_trades", 0) < min_trades:
            logger.error(f"Insufficient backtest trades: {results['total_trades']} < {min_trades}")
            return False
        
        if results.get("sharpe_ratio", 0) < min_sharpe:
            logger.error(f"Insufficient Sharpe ratio: {results['sharpe_ratio']:.2f} < {min_sharpe}")
            return False
        
        # Approve
        strategy.is_paper_trading = False
        strategy.user_confirmed = True
        logger.success(f"Strategy {strategy.name} approved for LIVE trading")
        
        return True
    
    def get_strategy_summary(self, strategy_id: str) -> str:
        """Generate human-readable summary of strategy and backtest."""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return f"Strategy {strategy_id} not found"
        
        summary = f"""
Strategy: {strategy.name}
ID: {strategy.strategy_id}
Description: {strategy.description}
Status: {'PAPER TRADING' if strategy.is_paper_trading else 'LIVE TRADING'}
User Confirmed: {strategy.user_confirmed}

Backtest Results:
"""
        if strategy.backtest_results:
            r = strategy.backtest_results
            summary += f"""
  Total Return: {r.get('total_return', 0):.2%}
  Sharpe Ratio: {r.get('sharpe_ratio', 0):.2f}
  Max Drawdown: {r.get('max_drawdown', 0):.2%}
  Win Rate: {r.get('win_rate', 0):.2%}
  Total Trades: {r.get('total_trades', 0)}
  Backtest Period: {r.get('backtest_period_days', 0)} days
"""
        else:
            summary += "  Not backtested yet\n"
        
        return summary
