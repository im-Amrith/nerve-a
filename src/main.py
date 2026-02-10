"""
Main entry point for the Agentic Brokerage OS.
"""

import os
from dotenv import load_dotenv
from loguru import logger

from core.orchestrator import Orchestrator
from core.state import UserConstitution


def setup_logging():
    """Configure logging with loguru."""
    logger.add(
        "logs/brokerage_os_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    logger.info("Logging initialized")


def load_configuration() -> dict:
    """Load configuration from environment."""
    load_dotenv()
    
    config = {
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "news_api_key": os.getenv("NEWS_API_KEY"),
        "sentinel_latency_ms": int(os.getenv("SENTINEL_LATENCY_MS", "50")),
        "perception_timeout_ms": int(os.getenv("PERCEPTION_TIMEOUT_MS", "200")),
    }
    
    # Validate required keys
    if not config["groq_api_key"]:
        raise ValueError("GROQ_API_KEY not found in environment")
    
    logger.info("Configuration loaded")
    return config


def create_default_constitution() -> UserConstitution:
    """Create default user constitution with sensible guardrails."""
    return UserConstitution(
        max_position_size=10000,
        max_daily_loss=5000,
        max_leverage=1.5,
        min_time_between_trades=60,
        max_trades_per_day=10,
        block_after_loss_streak=3,
        block_on_tilt=True,
        require_cooldown=True,
        cooldown_duration_minutes=30,
        trading_hours_only=True,
        strategies_require_backtest=True,
        min_backtest_trades=30,
        min_sharpe_ratio=1.0,
        enable_kill_switch=True
    )


def run_interactive_mode(orchestrator: Orchestrator):
    """Run in interactive mode for user commands."""
    logger.info("Starting interactive mode...")
    print("\n" + "="*60)
    print("🤖 AGENTIC BROKERAGE OS - INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  trade: <instruction>  - Execute a trade (e.g., 'trade: buy 10 AAPL')")
    print("  strategy: <prompt>    - Generate strategy (e.g., 'strategy: buy when RSI < 30')")
    print("  insights              - View trading insights")
    print("  exit                  - Exit the system")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                logger.info("Exiting interactive mode")
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == "insights":
                insights = orchestrator.journal.generate_insights(timeframe_days=30)
                print(f"\n📊 TRADING INSIGHTS:\n{insights}\n")
            
            elif user_input.lower().startswith("strategy:"):
                prompt = user_input[9:].strip()
                result = orchestrator.run_strategy_generation(prompt)
                print(f"\n✅ Strategy generated!")
                print(f"Name: {result['name']}")
                print(f"ID: {result['strategy_id']}")
                if result.get('backtest_results'):
                    bt = result['backtest_results']
                    print(f"\nBacktest Results:")
                    print(f"  Total Return: {bt['total_return']:.2%}")
                    print(f"  Sharpe Ratio: {bt['sharpe_ratio']:.2f}")
                    print(f"  Max Drawdown: {bt['max_drawdown']:.2%}")
                    print(f"  Win Rate: {bt['win_rate']:.2%}")
                    print(f"  Total Trades: {bt['total_trades']}\n")
            
            elif user_input.lower().startswith("trade:"):
                instruction = user_input[6:].strip()
                
                logger.info(f"Processing trade: {instruction}")
                final_state = orchestrator.run(instruction)
                
                # Display results
                if final_state.get("error_state"):
                    print(f"\n❌ ERROR: {final_state['error_state']}\n")
                elif final_state.get("kill_switch_active"):
                    sentinel = final_state.get("sentinel_result")
                    print(f"\n🚫 TRADE BLOCKED")
                    if sentinel:
                        print(f"Reason: {sentinel.reasoning}")
                        if sentinel.violated_rules:
                            print(f"Violations: {', '.join(sentinel.violated_rules)}\n")
                else:
                    print(f"\n✅ TRADE EXECUTED")
                    executed = final_state.get("executed_trades", [])
                    if executed:
                        trade = executed[-1]
                        print(f"Trade ID: {trade.trade_id}")
                        print(f"Action: {trade.intent.action.upper()}")
                        print(f"Symbol: {trade.intent.symbol}")
                        print(f"Quantity: {trade.intent.quantity}")
                        print(f"Status: {trade.status}\n")
            
            else:
                # Default: treat as trade instruction
                logger.info(f"Processing: {user_input}")
                final_state = orchestrator.run(user_input)
                
                if final_state.get("error_state"):
                    print(f"\n❌ ERROR: {final_state['error_state']}\n")
                else:
                    print(f"\n✅ Command processed\n")
        
        except KeyboardInterrupt:
            print("\n👋 Interrupted. Exiting...")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point."""
    setup_logging()
    
    logger.info("="*60)
    logger.info("🚀 AGENTIC BROKERAGE OS STARTING")
    logger.info("="*60)
    
    # Load configuration
    config = load_configuration()
    
    # Create user constitution
    constitution = create_default_constitution()
    logger.info(f"User constitution loaded: {constitution.dict()}")
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        groq_api_key=config["groq_api_key"],
        user_constitution=constitution,
        news_api_key=config.get("news_api_key")
    )
    
    logger.success("Orchestrator initialized successfully")
    
    # Run in interactive mode
    run_interactive_mode(orchestrator)
    
    logger.info("System shutdown complete")


if __name__ == "__main__":
    main()
