# app/etl/__main__.py
"""
Makes the ETL module runnable with: python -m app.etl.load_prices
"""
from .load_prices import load_prices

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(f"Loading {days} days of price history...")
    load_prices(days=days)