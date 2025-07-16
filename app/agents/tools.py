"""
LangChain tools that the agent can call.
They must match the JSON schema defined in `app/agents/schema.py`.
"""
from __future__ import annotations

import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text
from langchain.tools import Tool

from app.db import engine

def _fig_to_markdown(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    data = base64.b64encode(buf.getvalue()).decode("utf8")
    return f"![plot](data:image/png;base64,{data})"

def get_top_movers(period: str = "7d", limit: int = 5) -> str:
    days_map = {"1d": 1, "7d": 7, "30d": 30}
    days = days_map.get(period, 7)
    query = text(
        """
        WITH window AS (
            SELECT
              coin_id,
              symbol,
              date,
              price,
              FIRST_VALUE(price) OVER (PARTITION BY coin_id ORDER BY date) AS price_start
            FROM prices
            WHERE date >= CURRENT_DATE - :days
        )
        SELECT
          symbol,
          ROUND(100 * (MAX(price) - MIN(price_start)) / MIN(price_start), 2) AS pct_change
        FROM window
        GROUP BY symbol
        ORDER BY pct_change DESC
        LIMIT :limit
        """
    )
    df = pd.read_sql(query, engine, params={"days": days, "limit": limit})
    if df.empty:
        return "No data yet – run the ETL loader first."
    table_md = df.to_markdown(index=False)
    return f"Top {limit} movers over the last {period}:\n\n{table_md}"

def plot_price(coin: str = "BTC", days: int = 30) -> str:
    query = text(
        """
        SELECT date, price
        FROM prices
        WHERE symbol ILIKE :sym
          AND date >= CURRENT_DATE - :days
        ORDER BY date
        """
    )
    df = pd.read_sql(query, engine, params={"sym": coin, "days": days})
    if df.empty:
        return f"No price data found for {coin}."
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["price"], marker="o")
    ax.set_title(f"{coin.upper()} price – last {days} days")
    ax.set_xlabel("Date")
    ax.set_ylabel("USD")
    fig.autofmt_xdate()
    return _fig_to_markdown(fig)

def sql_tool() -> list[Tool]:
    tools = [
        Tool.from_function(
            name="get_top_movers",
            func=get_top_movers,
            description="Get top N coins by percentage gain over a period.",
        ),
        Tool.from_function(
            name="plot_price",
            func=plot_price,
            description="Plot price history for a given coin symbol.",
        ),
    ]
    return tools
