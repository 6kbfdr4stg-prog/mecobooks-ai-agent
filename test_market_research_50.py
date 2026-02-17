#!/usr/bin/env python3
"""
Test script to run market research with 50 books requirement
"""
import os
import sys
from datetime import datetime

# Set environment variable for Google Sheets webhook
os.environ['GOOGLE_SHEETS_WEBHOOK_URL'] = 'https://script.google.com/macros/s/AKfycbyBgIl9-C-vFxPGh9V70iZQEP25vv_uCa223ogvZ6DwCHiKnaTBpJSIvPw0koeGgdYvyw/exec'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after setting up path
from ai_agents.market_research import MarketResearchAgent

if __name__ == "__main__":
    print("🚀 Running Market Research Agent with 50-book requirement...")
    agent = MarketResearchAgent()
    agent.run()
    print("✅ Market research completed!")
