import os, httpx, pandas as pd
from dotenv import load_dotenv
from app.db import engine, init_db

load_dotenv()

API_KEY = os.getenv("COINGECKO_API_KEY")
URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
}

HEADERS = {"x-cg-demo-api-key": API_KEY}  # CoinGecko requires this header

def fetch() -> pd.DataFrame:
    r = httpx.get(URL, params=PARAMS, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)[
        ["id", "symbol", "current_price", "market_cap", "total_volume"]
    ]
    df["date"] = pd.Timestamp.utcnow().date()
    df.columns = ["coin_id", "symbol", "price", "market_cap", "volume", "date"]
    return df
