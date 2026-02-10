"""
Strategy Generation Demo
Demonstrates natural language to backtested trading algorithms.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.engines.strategy_engine import StrategyEngine


def run_strategy_generation_demo(groq_api_key: str):
    """
    Demo: Convert natural language trading ideas into executable strategies.
    """
    print("="*80)
    print("🧠 STRATEGY GENERATION DEMO: Text-to-Algo")
    print("="*80)
    print("\nThis demonstrates converting natural language trading ideas into")
    print("executable, backtested Python strategies with automatic safety checks.")
    print("\n" + "="*80 + "\n")
    
    engine = StrategyEngine(groq_api_key)
    
    # Define test strategies
    test_strategies = [
        "Buy when RSI goes below 30, sell when it goes above 70",
        "Buy when 20-day moving average crosses above 50-day moving average",
        "Buy when price drops 5% in a single day with high volume"
    ]
    
    for i, prompt in enumerate(test_strategies, 1):
        print(f"\n{'─'*80}")
        print(f"STRATEGY #{i}: {prompt}")
        print(f"{'─'*80}\n")
        
        print("🔄 Generating strategy code...")
        try:
            strategy = engine.generate_strategy(prompt, auto_backtest=True)
            
            print(f"✅ Strategy generated: {strategy.name}")
            print(f"   ID: {strategy.strategy_id}")
            print(f"   Status: {'PAPER TRADING' if strategy.is_paper_trading else 'LIVE'}")
            
            print("\n📝 Generated Code Preview:")
            print("   " + "-"*60)
            code_lines = strategy.generated_code.split('\n')[:15]
            for line in code_lines:
                print(f"   {line}")
            if len(strategy.generated_code.split('\n')) > 15:
                print(f"   ... ({len(strategy.generated_code.split('\n')) - 15} more lines)")
            print("   " + "-"*60)
            
            if strategy.backtest_results:
                print("\n📊 Backtest Results:")
                bt = strategy.backtest_results
                
                if bt.get("status") == "success":
                    print(f"   Total Return:     {bt['total_return']:>10.2%}")
                    print(f"   Sharpe Ratio:     {bt['sharpe_ratio']:>10.2f}")
                    print(f"   Max Drawdown:     {bt['max_drawdown']:>10.2%}")
                    print(f"   Win Rate:         {bt['win_rate']:>10.2%}")
                    print(f"   Total Trades:     {bt['total_trades']:>10}")
                    print(f"   Backtest Period:  {bt['backtest_period_days']:>10} days")
                    
                    # Determine if meets minimum requirements
                    meets_requirements = (
                        bt['total_trades'] >= 30 and
                        bt['sharpe_ratio'] >= 1.0
                    )
                    
                    if meets_requirements:
                        print("\n   ✅ MEETS REQUIREMENTS for live trading approval")
                    else:
                        print("\n   ⚠️  Does NOT meet requirements:")
                        if bt['total_trades'] < 30:
                            print(f"      - Insufficient trades: {bt['total_trades']} < 30")
                        if bt['sharpe_ratio'] < 1.0:
                            print(f"      - Low Sharpe ratio: {bt['sharpe_ratio']:.2f} < 1.0")
                else:
                    print(f"   ❌ Backtest failed: {bt.get('error', 'Unknown error')}")
            
            print(f"\n{'─'*80}\n")
            
        except Exception as e:
            print(f"❌ Strategy generation failed: {e}\n")
    
    # Demo approval workflow
    print("\n" + "="*80)
    print("🔐 APPROVAL WORKFLOW DEMO")
    print("="*80)
    print("\nDemonstrating safety checks before live trading approval...\n")
    
    all_strategies = list(engine.strategies.values())
    
    if all_strategies:
        test_strategy = all_strategies[0]
        print(f"Attempting to approve strategy: {test_strategy.name}")
        print(f"Current status: {'PAPER' if test_strategy.is_paper_trading else 'LIVE'}")
        
        print("\n🛡️  Running approval checks...")
        approved = engine.approve_for_live_trading(test_strategy.strategy_id)
        
        if approved:
            print("✅ Strategy APPROVED for live trading")
            print("   User confirmation required: YES")
            print("   Status changed: PAPER → LIVE")
        else:
            print("❌ Strategy NOT approved for live trading")
            print("   Reason: Does not meet minimum requirements")
            print("   Remains in: PAPER TRADING mode")
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"\nTotal strategies generated: {len(engine.strategies)}")
    print(f"Paper trading: {sum(1 for s in engine.strategies.values() if s.is_paper_trading)}")
    print(f"Live approved: {sum(1 for s in engine.strategies.values() if not s.is_paper_trading)}")
    
    print("\n💡 KEY FEATURES DEMONSTRATED:")
    print("   ✓ Natural language to executable Python code")
    print("   ✓ Automatic syntax validation and security checks")
    print("   ✓ Backtesting with realistic P&L simulation")
    print("   ✓ Minimum requirements enforcement (30+ trades, Sharpe >1.0)")
    print("   ✓ Default paper trading with explicit live approval")
    print("   ✓ User confirmation required for live execution")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        print("❌ Error: GROQ_API_KEY not found in environment")
        print("Please set GROQ_API_KEY in your .env file")
    else:
        run_strategy_generation_demo(groq_key)
