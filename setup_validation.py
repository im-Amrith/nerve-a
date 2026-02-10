"""
Setup and validation script for Agentic Brokerage OS
Run this after installation to verify everything is configured correctly.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Verify Python version >= 3.10"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (requires 3.10+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    # Map package names to their import names
    required = {
        "langgraph": "langgraph",
        "langchain": "langchain",
        "groq": "groq",
        "opencv-python-headless": "cv2",
        "Pillow": "PIL",
        "pandas": "pandas",
        "numpy": "numpy",
        "pydantic": "pydantic",
        "loguru": "loguru"
    }
    
    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_environment():
    """Check environment variables"""
    print("\nChecking environment configuration...")
    
    # Check .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("  ⚠️  .env file not found")
        print("     Copy .env.example to .env and configure")
        
        # Try to read from .env.example
        if Path(".env.example").exists():
            print("  📝 Creating .env from .env.example...")
            import shutil
            shutil.copy(".env.example", ".env")
            print("  ✅ Created .env (please edit and add your API keys)")
    else:
        print("  ✅ .env file exists")
    
    # Load and check keys
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and not groq_key.startswith("your_"):
        print("  ✅ GROQ_API_KEY is set")
        key_valid = True
    else:
        print("  ❌ GROQ_API_KEY not configured")
        print("     Get your key from: https://console.groq.com/keys")
        key_valid = False
    
    # Optional keys
    news_key = os.getenv("NEWS_API_KEY")
    if news_key and not news_key.startswith("your_"):
        print("  ✅ NEWS_API_KEY is set (optional)")
    else:
        print("  ℹ️  NEWS_API_KEY not set (optional, for news sentiment)")
    
    pinecone_key = os.getenv("PINECONE_API_KEY")
    if pinecone_key and not pinecone_key.startswith("your_"):
        print("  ✅ PINECONE_API_KEY is set (optional)")
    else:
        print("  ℹ️  PINECONE_API_KEY not set (optional, for vector memory)")
    
    return key_valid


def check_directories():
    """Create necessary directories"""
    print("\nChecking directory structure...")
    
    dirs = ["logs", "screenshots", "config", "data"]
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  📁 Creating {dir_name}/")
            dir_path.mkdir(exist_ok=True)
    
    return True


def test_groq_connection():
    """Test Groq API connection"""
    print("\nTesting Groq API connection...", end=" ")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key or groq_key.startswith("your_"):
            print("⏭️  Skipped (no API key)")
            return True  # Don't fail the setup
        
        from groq import Groq
        client = Groq(api_key=groq_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'ready' if you can read this."}],
            max_tokens=10
        )
        
        if response.choices:
            print("✅ Connection successful")
            return True
        else:
            print("❌ Connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_imports():
    """Test critical imports"""
    print("\nTesting project imports...")
    
    try:
        print("  Importing core modules...", end=" ")
        from src.core.state import AgentState, UserConstitution
        from src.core.perception import PerceptionEngine
        from src.core.orchestrator import Orchestrator
        print("✅")
        
        print("  Importing engines...", end=" ")
        from src.engines.pre_trade_sentinel import PreTradeSentinel
        from src.engines.strategy_engine import StrategyEngine
        from src.engines.rag_journal import RAGJournal
        print("✅")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def run_quick_test():
    """Run a quick functionality test"""
    print("\nRunning functionality test...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from src.core.state import UserConstitution
        
        print("  Creating user constitution...", end=" ")
        constitution = UserConstitution(
            max_position_size=10000,
            enable_kill_switch=True
        )
        print("✅")
        
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and not groq_key.startswith("your_"):
            from src.engines.pre_trade_sentinel import PreTradeSentinel
            from src.core.state import TradeIntent
            from datetime import datetime
            
            print("  Testing sentinel...", end=" ")
            sentinel = PreTradeSentinel(groq_key, constitution)
            
            intent = TradeIntent(
                action="buy",
                symbol="TEST",
                quantity=10,
                order_type="market",
                timestamp=datetime.now()
            )
            
            result = sentinel.check_trade(intent, {"total_value": 100000})
            
            if result and hasattr(result, 'inference_time_ms'):
                print(f"✅ ({result.inference_time_ms:.1f}ms)")
            else:
                print("✅")
        else:
            print("  Sentinel test skipped (no API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup validation"""
    print("="*70)
    print("🚀 AGENTIC BROKERAGE OS - SETUP VALIDATION")
    print("="*70)
    
    results = []
    
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Environment", check_environment()))
    results.append(("Directories", check_directories()))
    results.append(("Groq Connection", test_groq_connection()))
    results.append(("Project Imports", test_imports()))
    results.append(("Functionality", run_quick_test()))
    
    print("\n" + "="*70)
    print("📊 SETUP VALIDATION RESULTS")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<30} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 Setup validation complete! You're ready to go.")
        print("\nNext steps:")
        print("  1. Run demos: python demos/ui_adaptation_demo.py")
        print("  2. Start interactive mode: python src/main.py")
        print("  3. Read docs: docs/QUICKSTART.md")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("   See docs/QUICKSTART.md for troubleshooting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
