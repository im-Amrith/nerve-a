"""
Pre-Trade Sentinel Demo
Demonstrates the kill switch blocking risky trades in <50ms.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.engines.pre_trade_sentinel import PreTradeSentinel
from src.core.state import UserConstitution, TradeIntent


def run_sentinel_demo(groq_api_key: str):
    """
    Demo: Real-time trade safety checks and kill switch.
    """
    print("="*80)
    print("🛡️  PRE-TRADE SENTINEL DEMO: Kill Switch in Action")
    print("="*80)
    print("\nThis demonstrates sub-50ms safety checks that block risky trades")
    print("before they reach the exchange, preventing emotional trading losses.")
    print("\n" + "="*80 + "\n")
    
    # Create user constitution with strict rules
    constitution = UserConstitution(
        max_position_size=5000,
        max_daily_loss=2000,
        max_leverage=1.5,
        min_time_between_trades=30,
        max_trades_per_day=5,
        block_after_loss_streak=2,
        block_on_tilt=True,
        enable_kill_switch=True
    )
    
    sentinel = PreTradeSentinel(groq_api_key, constitution)
    
    # Simulated portfolio
    portfolio = {
        "total_value": 50000,
        "cash": 25000,
        "positions": {"AAPL": 100},
        "current_prices": {"AAPL": 150, "TSLA": 200, "MSFT": 300}
    }
    
    print("📋 USER CONSTITUTION:")
    print(f"   Max Position Size:     ${constitution.max_position_size:,}")
    print(f"   Max Daily Loss:        ${constitution.max_daily_loss:,}")
    print(f"   Max Leverage:          {constitution.max_leverage}x")
    print(f"   Min Time Between:      {constitution.min_time_between_trades}s")
    print(f"   Max Trades/Day:        {constitution.max_trades_per_day}")
    print(f"   Loss Streak Limit:     {constitution.block_after_loss_streak}")
    print(f"   Kill Switch Enabled:   {constitution.enable_kill_switch}")
    
    print(f"\n💼 CURRENT PORTFOLIO:")
    print(f"   Total Value:  ${portfolio['total_value']:,}")
    print(f"   Cash:         ${portfolio['cash']:,}")
    print(f"   Positions:    {portfolio['positions']}")
    
    # Test cases
    test_cases = [
        {
            "name": "Normal Trade (Should Pass)",
            "trade": TradeIntent(
                action="buy",
                symbol="MSFT",
                quantity=10,
                order_type="limit",
                price=300.0,
                timestamp=datetime.now()
            ),
            "expected": "approved"
        },
        {
            "name": "Over-Sized Position (Should Block)",
            "trade": TradeIntent(
                action="buy",
                symbol="TSLA",
                quantity=100,  # 100 * $200 = $20,000 > limit
                order_type="market",
                timestamp=datetime.now()
            ),
            "expected": "blocked"
        },
        {
            "name": "Excessive Leverage (Should Block)",
            "trade": TradeIntent(
                action="buy",
                symbol="AAPL",
                quantity=300,  # Would create 2x leverage
                order_type="market",
                timestamp=datetime.now()
            ),
            "expected": "blocked"
        },
        {
            "name": "Too Soon After Last Trade (Should Block)",
            "trade": TradeIntent(
                action="buy",
                symbol="MSFT",
                quantity=5,
                order_type="market",
                timestamp=datetime.now(),  # Immediately after previous
            ),
            "expected": "blocked"
        }
    ]
    
    print("\n" + "="*80)
    print("🎯 RUNNING TEST CASES")
    print("="*80)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST CASE #{i}: {test['name']}")
        print(f"{'─'*80}")
        
        trade = test["trade"]
        print(f"\n📝 Trade Details:")
        print(f"   Action:      {trade.action.upper()}")
        print(f"   Symbol:      {trade.symbol}")
        print(f"   Quantity:    {trade.quantity}")
        print(f"   Order Type:  {trade.order_type}")
        print(f"   Price:       ${trade.price or 'Market'}")
        
        print(f"\n⏱️  Running sentinel checks...")
        
        result = sentinel.check_trade(trade, portfolio)
        results.append({
            "test": test["name"],
            "expected": test["expected"],
            "actual": "approved" if result.approved else "blocked",
            "latency_ms": result.inference_time_ms
        })
        
        print(f"\n📊 RESULT:")
        print(f"   Status:           {'✅ APPROVED' if result.approved else '🚫 BLOCKED'}")
        print(f"   Latency:          {result.inference_time_ms:.2f} ms")
        print(f"   Risk Score:       {result.risk_score:.2f}/1.0")
        print(f"   Recommendation:   {result.recommended_action.upper()}")
        
        if result.violated_rules:
            print(f"\n   ⚠️  VIOLATIONS ({len(result.violated_rules)}):")
            for rule in result.violated_rules:
                print(f"      • {rule}")
        
        print(f"\n   💭 Reasoning:")
        print(f"      {result.reasoning}")
        
        # Latency check
        if result.inference_time_ms > 50:
            print(f"\n   ⚠️  WARNING: Latency {result.inference_time_ms:.2f}ms exceeds 50ms target!")
        else:
            print(f"\n   ✅ Latency within target (<50ms)")
        
        # Add small delay between trades to avoid min_time_between_trades violations
        import time
        time.sleep(0.1)
    
    # Results summary
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    
    print("\n┌────────────────────────────────────┬──────────┬──────────┬───────────┐")
    print("│ Test Case                          │ Expected │ Actual   │ Latency   │")
    print("├────────────────────────────────────┼──────────┼──────────┼───────────┤")
    
    for r in results:
        name = r["test"][:34].ljust(34)
        expected = r["expected"][:8].ljust(8)
        actual = r["actual"][:8].ljust(8)
        latency = f"{r['latency_ms']:.1f}ms".ljust(9)
        
        match = "✓" if r["expected"] == r["actual"] else "✗"
        print(f"│ {name} │ {expected} │ {actual} │ {latency} │ {match}")
    
    print("└────────────────────────────────────┴──────────┴──────────┴───────────┘")
    
    # Performance metrics
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    max_latency = max(r["latency_ms"] for r in results)
    within_target = sum(1 for r in results if r["latency_ms"] < 50)
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"   Average Latency:  {avg_latency:.2f} ms")
    print(f"   Max Latency:      {max_latency:.2f} ms")
    print(f"   Within Target:    {within_target}/{len(results)} ({within_target/len(results)*100:.0f}%)")
    
    accuracy = sum(1 for r in results if r["expected"] == r["actual"]) / len(results)
    print(f"   Accuracy:         {accuracy*100:.0f}%")
    
    print("\n💡 KEY FEATURES DEMONSTRATED:")
    print("   ✓ Sub-50ms inference for real-time safety checks")
    print("   ✓ Multi-dimensional risk scoring (position size, leverage, timing)")
    print("   ✓ Hard kill switch blocks trades violating user constitution")
    print("   ✓ Behavioral guards against tilt/emotional trading")
    print("   ✓ Comprehensive rule violation tracking and reporting")
    print("   ✓ Deterministic checks + LLM reasoning for edge cases")
    
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
        run_sentinel_demo(groq_key)
