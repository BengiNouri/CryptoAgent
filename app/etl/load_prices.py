# app/etl/load_prices.py
import os
import time
import httpx
import pandas as pd
from sqlalchemy import text
from app.db import engine, init_db

COINS = ["bitcoin","ethereum","solana"]  # whatever you like
API = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

def fetch_history(coin_id: str, days: int = 30) -> pd.DataFrame:
    params = {"vs_currency": "usd", "days": days}
    resp = httpx.get(API.format(id=coin_id), params=params, timeout=10)
    resp.raise_for_status()  # Raise an exception for bad status codes
    
    json_data = resp.json()
    print(f"API Response keys for {coin_id}: {list(json_data.keys())}")
    
    # Check if 'prices' key exists, if not print the response for debugging
    if "prices" not in json_data:
        print(f"Error: 'prices' key not found in response for {coin_id}")
        print(f"Response: {json_data}")
        # Try alternative approach - sometimes the API returns different structure
        if "error" in json_data:
            raise Exception(f"CoinGecko API Error: {json_data['error']}")
        else:
            raise KeyError(f"Expected 'prices' key not found in API response for {coin_id}")
    
    data = json_data["prices"]  # list of [timestamp, price]
    df = pd.DataFrame(data, columns=["ts","price"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms").dt.date
    df["coin_id"] = coin_id
    df["symbol"] = coin_id.upper()
    return df[["coin_id","symbol","date","price"]]

def load_prices(days: int = 30):
    # Ensure database is initialized before loading data
    init_db()
    
    for coin in COINS:
        df = fetch_history(coin, days=days)
        with engine.begin() as conn:
            # simple upsert: delete old, insert fresh
            conn.execute(
                text("DELETE FROM prices WHERE coin_id = :cid AND date >= CURRENT_DATE - :d"),
                {"cid": coin, "d": days}
            )
            conn.execute(
                text("""
                  INSERT INTO prices (coin_id,symbol,date,price)
                  VALUES (:coin_id,:symbol,:date,:price)
                """),
                df.to_dict(orient="records")
            )
        time.sleep(1)  # throttle
    print("✅ Loaded latest prices")

if __name__ == "__main__":
    load_prices(days=30)
    