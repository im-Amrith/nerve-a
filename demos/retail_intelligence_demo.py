"""
Demo: Retail Intelligence Layer - Multi-agent institutional-grade market intelligence.
Shows how multiple specialized agents work together to reduce information asymmetry.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from loguru import logger

from src.engines.retail_intelligence import RetailIntelligenceLayer

# Load environment
load_dotenv()

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO", format="<level>{message}</level>")


async def main():
    """Demonstrate the Retail Intelligence Layer in action."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           RETAIL INTELLIGENCE LAYER DEMONSTRATION                    ║
║                                                                      ║
║  Multi-Agent Swarm for Institutional-Grade Market Intelligence      ║
║  Monitors: News, Sentiment, Technicals, Volatility                  ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    news_key = os.getenv("NEWS_API_KEY")
    
    if not groq_key:
        logger.error("GROQ_API_KEY not found in .env file!")
        logger.error("Please add: GROQ_API_KEY=your_key_here")
        return
    
    logger.info("✓ GROQ_API_KEY configured")
    
    if not news_key:
        logger.warning("⚠ NEWS_API_KEY not configured (optional)")
        logger.warning("  Add NEWS_API_KEY to .env for real news integration")
    else:
        logger.info("✓ NEWS_API_KEY configured")
    
    print()
    
    # Initialize intelligence layer
    logger.info("Initializing Retail Intelligence Layer...")
    intel = RetailIntelligenceLayer(
        groq_api_key=groq_key,
        news_api_key=news_key
    )
    
    logger.info(f"✓ Initialized {len(intel.agents)} specialized agents:")
    for agent in intel.agents:
        logger.info(f"  - {agent.name}")
    
    print("\n" + "="*70 + "\n")
    
    # Demo 1: Single stock intelligence
    symbol = "AAPL"
    logger.info(f"Gathering intelligence for {symbol}...")
    logger.info("Deploying agent swarm (NewsAgent, SentimentAgent, TechnicalAgent, VolatilityAgent)...\n")
    
    report = await intel.gather_intelligence(symbol)
    
    # Show terminal view
    terminal = intel.generate_terminal_view(report)
    print(terminal)
    
    print("\n" + "="*70 + "\n")
    
    # Demo 2: Compare multiple symbols
    logger.info("Multi-Symbol Intelligence Comparison")
    logger.info("="*70)
    
    symbols = ["AAPL", "TSLA", "NVDA"]
    logger.info(f"Analyzing: {', '.join(symbols)}\n")
    
    # Gather intelligence for all symbols concurrently
    tasks = [intel.gather_intelligence(sym) for sym in symbols]
    reports = await asyncio.gather(*tasks)
    
    # Compare risk scores
    logger.info("RISK COMPARISON:")
    logger.info("-" * 70)
    
    for sym, rep in zip(symbols, reports):
        synthesis = rep.get("synthesis", {})
        risk = synthesis.get("risk_score", 0)
        confidence = synthesis.get("confidence", 0)
        
        bar = "█" * int(risk) + "░" * (10 - int(risk))
        logger.info(f"{sym:6} | Risk: [{bar}] {risk}/10 | Confidence: {confidence}%")
    
    print("\n" + "="*70 + "\n")
    
    # Demo 3: Show raw intelligence breakdown
    logger.info("RAW INTELLIGENCE BREAKDOWN")
    logger.info("="*70)
    
    sample_report = reports[0]
    raw_intel = sample_report.get("raw_intelligence", [])
    
    for intel_data in raw_intel:
        source = intel_data.get("source", "Unknown")
        logger.info(f"\n{source}:")
        
        if source == "NewsAgent":
            headlines = intel_data.get("headlines", [])
            count = len(headlines) if isinstance(headlines, list) else 0
            logger.info(f"  - Headlines captured: {count}")
            if isinstance(headlines, list):
                for h in headlines[:2]:
                    if isinstance(h, dict):
                        logger.info(f"    • {h.get('title', 'N/A')[:60]}...")
        
        elif source == "SentimentAgent":
            sentiment = intel_data.get("overall_sentiment", "N/A")
            score = intel_data.get("sentiment_score", 0)
            confidence = intel_data.get("confidence", 0)
            logger.info(f"  - Overall: {sentiment}")
            logger.info(f"  - Score: {score:.2f}")
            logger.info(f"  - Confidence: {confidence:.0%}")
        
        elif source == "TechnicalAgent":
            indicators = intel_data.get("indicators", {})
            signals = intel_data.get("signals", [])
            logger.info(f"  - RSI: {indicators.get('rsi', 0):.1f}")
            logger.info(f"  - MACD: {indicators.get('macd', 0):.2f}")
            logger.info(f"  - Volume Ratio: {indicators.get('volume_ratio', 0):.2f}")
            logger.info(f"  - Signals: {len(signals)}")
            for sig in signals[:2]:
                logger.info(f"    • {sig}")
        
        elif source == "VolatilityAgent":
            vol = intel_data.get("volatility", {})
            regime = intel_data.get("regime", "N/A")
            risk = intel_data.get("risk_level", "N/A")
            logger.info(f"  - Historical Vol: {vol.get('historical', 0):.1%}")
            logger.info(f"  - Implied Vol: {vol.get('implied', 0):.1%}")
            logger.info(f"  - Regime: {regime}")
            logger.info(f"  - Risk Level: {risk}")
    
    print("\n" + "="*70 + "\n")
    
    # Demo 4: Show synthesis
    logger.info("AI SYNTHESIS")
    logger.info("="*70)
    
    synthesis = sample_report.get("synthesis", {})
    
    logger.info(f"\nSummary:")
    summary = synthesis.get("summary", "No summary available")
    # Wrap text
    words = summary.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > 70:
            logger.info(f"  {line}")
            line = word + " "
        else:
            line += word + " "
    if line:
        logger.info(f"  {line}")
    
    logger.info(f"\nKey Signals:")
    for i, signal in enumerate(synthesis.get("key_signals", []), 1):
        logger.info(f"  {i}. {signal}")
    
    logger.info(f"\nInstitutional Edge:")
    edge = synthesis.get("institutional_edge", "N/A")
    logger.info(f"  {edge}")
    
    logger.info(f"\nRecommended Actions:")
    for i, action in enumerate(synthesis.get("recommended_actions", []), 1):
        logger.info(f"  {i}. {action}")
    
    print("\n" + "="*70 + "\n")
    
    logger.info("✓ Demo complete!")
    logger.info("\nThe Retail Intelligence Layer demonstrates:")
    logger.info("  • Multi-agent parallel intelligence gathering")
    logger.info("  • LLM-powered synthesis of diverse data sources")
    logger.info("  • Institutional-grade insights for retail traders")
    logger.info("  • Reduction of information asymmetry")


if __name__ == "__main__":
    asyncio.run(main())
