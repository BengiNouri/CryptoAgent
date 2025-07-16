#!/usr/bin/env python3
"""
Management script for crypto-insight-agent
Usage:
  python manage.py migrate        # Run database migrations
  python manage.py load-data      # Load crypto price data
  python manage.py load-data 7    # Load 7 days of data
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import init_db
from app.etl.load_prices import load_prices

def migrate():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    init_db()
    print("✅ Database migrations complete")

def load_data(days=30):
    """Load crypto price data"""
    print(f"📊 Loading {days} days of crypto price data...")
    load_prices(days=days)
    print("✅ Data loading complete")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        migrate()
    elif command == "load-data":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        load_data(days)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()