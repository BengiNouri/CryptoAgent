#!/usr/bin/env python3
"""
Test script to verify all tools are working correctly
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.tools import get_top_movers, plot_price
from app.agents.insight_agent import ask

def test_tools():
    print("🧪 Testing Crypto Insight Agent Tools")
    print("=" * 50)
    
    # Test get_top_movers
    print("\n📊 Testing get_top_movers...")
    try:
        result = get_top_movers("7d", 3)
        print("✅ get_top_movers SUCCESS")
        print(result[:200] + "..." if len(result) > 200 else result)
    except Exception as e:
        print(f"❌ get_top_movers FAILED: {e}")
    
    # Test plot_price
    print("\n📈 Testing plot_price...")
    try:
        result = plot_price("BITCOIN", 7)
        print("✅ plot_price SUCCESS")
        print(f"Generated chart with {len(result)} characters")
    except Exception as e:
        print(f"❌ plot_price FAILED: {e}")
    
    # Test AI agent
    print("\n🤖 Testing AI agent...")
    try:
        result = ask("Show me the top 3 movers over 7 days")
        print("✅ AI agent SUCCESS")
        print(f"Agent response: {result}")
    except Exception as e:
        print(f"❌ AI agent FAILED: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    test_tools()