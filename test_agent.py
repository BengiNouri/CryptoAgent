#!/usr/bin/env python3
"""Quick test script for the crypto insight agent"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.insight_agent import ask

def test_agent():
    print("🧪 Testing Crypto Insight Agent...")
    print("=" * 50)
    
    # Test 1: Top movers
    print("\n1. Testing top movers query...")
    response1 = ask("Show me the top 3 movers over 7 days")
    print(f"Response: {response1}")
    
    # Test 2: Price chart
    print("\n2. Testing price chart query...")
    response2 = ask("Plot Bitcoin price for 30 days")
    print(f"Response: {response2}")
    
    # Test 3: General question
    print("\n3. Testing general question...")
    response3 = ask("What is Bitcoin?")
    print(f"Response: {response3}")
    
    print("\n" + "=" * 50)
    print("✅ Agent testing complete!")

if __name__ == "__main__":
    test_agent()