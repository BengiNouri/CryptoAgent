"""
LangChain tools that the agent can call.
They must match the JSON schema defined in `app/agents/schema.py`.
"""
from __future__ import annotations

import io
import base64
import logging
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text
from langchain.tools import Tool

from app.db import engine

# Import ML forecasting with fallback
try:
    from app.ml.forecasting import get_ml_insights, CryptoForecaster
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _fig_to_markdown(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    data = base64.b64encode(buf.getvalue()).decode("utf8")
    return f"![plot](data:image/png;base64,{data})"

def get_top_movers(period: str = "7d", limit: int = 5) -> str:
    try:
        days_map = {"1d": 1, "7d": 7, "30d": 30}
        days = days_map.get(period, 7)
        
        # Fixed: renamed 'window' to 'price_data' to avoid reserved keyword conflict
        # Also fixed INTERVAL syntax to work with parameter binding
        query = text(
            """
            WITH price_data AS (
                SELECT
                  coin_id,
                  symbol,
                  date,
                  price,
                  FIRST_VALUE(price) OVER (PARTITION BY coin_id ORDER BY date) AS price_start
                FROM prices
                WHERE date >= CURRENT_DATE - INTERVAL '1 day' * :days
            )
            SELECT
              symbol,
              ROUND(100 * (MAX(price) - MIN(price_start)) / MIN(price_start), 2) AS pct_change
            FROM price_data
            GROUP BY symbol
            ORDER BY pct_change DESC
            LIMIT :limit
            """
        )
        
        logger.info(f"Executing get_top_movers query for period={period}, limit={limit}")
        df = pd.read_sql(query, engine, params={"days": days, "limit": limit})
        
        if df.empty:
            logger.warning("No data returned from get_top_movers query")
            return "No data yet – run the ETL loader first."
        
        table_md = df.to_markdown(index=False)
        logger.info(f"Successfully retrieved {len(df)} top movers")
        return f"Top {limit} movers over the last {period}:\n\n{table_md}"
        
    except Exception as e:
        logger.error(f"Error in get_top_movers: {str(e)}")
        return f"Error retrieving top movers: {str(e)}"



def plot_price(coin: str = "bitcoin", days: int = 30) -> str:
    try:
        # Map common coin names to our database coin_ids
        coin_map = {
            "bitcoin": "bitcoin",
            "btc": "bitcoin", 
            "ethereum": "ethereum",
            "eth": "ethereum",
            "solana": "solana",
            "sol": "solana"
        }
        
        coin_id = coin_map.get(coin.lower(), coin.lower())
        
        # Fixed INTERVAL syntax to work with parameter binding
        query = text(
            """
            SELECT date, price
            FROM prices
            WHERE coin_id = :coin_id
              AND date >= CURRENT_DATE - INTERVAL '1 day' * :days
            ORDER BY date
            """
        )
        
        logger.info(f"Executing plot_price query for coin={coin} (mapped to {coin_id}), days={days}")
        df = pd.read_sql(query, engine, params={"coin_id": coin_id, "days": days})
        
        if df.empty:
            logger.warning(f"No price data found for {coin}")
            return f"No price data found for {coin}."
        
        fig, ax = plt.subplots()
        ax.plot(df["date"], df["price"], marker="o")
        ax.set_title(f"{coin.upper()} price – last {days} days")
        ax.set_xlabel("Date")
        ax.set_ylabel("USD")
        fig.autofmt_xdate()
        
        result = _fig_to_markdown(fig)
        logger.info(f"Successfully generated price chart for {coin} with {len(df)} data points")
        return result
        
    except Exception as e:
        logger.error(f"Error in plot_price: {str(e)}")
        return f"Error generating price chart: {str(e)}"

def forecast_price(coin: str = "bitcoin", days: int = 7) -> str:
    try:
        # Map common coin names to our database coin_ids
        coin_map = {
            "bitcoin": "bitcoin",
            "btc": "bitcoin", 
            "ethereum": "ethereum",
            "eth": "ethereum",
            "solana": "solana",
            "sol": "solana"
        }
        
        coin_id = coin_map.get(coin.lower(), coin.lower())
        
        # Get historical data for ML training
        query = text(
            """
            SELECT date, price
            FROM prices
            WHERE coin_id = :coin_id
            ORDER BY date
            """
        )
        
        logger.info(f"Executing forecast_price query for coin={coin} (mapped to {coin_id}), days={days}")
        df = pd.read_sql(query, engine, params={"coin_id": coin_id})
        
        if df.empty:
            logger.warning(f"No price data found for {coin}")
            return f"No price data found for {coin}."
        
        if len(df) < 30:
            return f"Insufficient data for forecasting {coin}. Need at least 30 days of data."
        
        # Generate ML insights and forecasts
        insights = get_ml_insights(df, coin.upper())
        
        # Format the results
        result = f"🔮 **ML Price Forecast for {coin.upper()}**\n\n"
        
        if 'price_forecast' in insights:
            forecast_data = insights['price_forecast']
            forecasts = forecast_data['forecasts']
            
            result += f"**📈 {days}-Day Price Predictions:**\n"
            current_price = df['price'].iloc[-1]
            
            for i, pred_price in enumerate(forecasts[:days], 1):
                change_pct = ((pred_price - current_price) / current_price) * 100
                direction = "📈" if change_pct > 0 else "📉"
                result += f"Day {i}: ${pred_price:.2f} ({direction} {change_pct:+.1f}%)\n"
        
        if 'trend_analysis' in insights:
            trend = insights['trend_analysis']
            result += f"\n**📊 Technical Analysis:**\n"
            result += f"• Trend: {trend.get('trend_direction', 'N/A').title()}\n"
            result += f"• 30-day change: {trend.get('price_change_30d', 0):.1f}%\n"
            result += f"• RSI: {trend.get('rsi', 0):.1f} ({trend.get('rsi_signal', 'N/A')})\n"
            result += f"• Support: ${trend.get('support_level', 0):.2f}\n"
            result += f"• Resistance: ${trend.get('resistance_level', 0):.2f}\n"
        
        if 'model_performance' in insights:
            perf = insights['model_performance']
            result += f"\n**🎯 Model Accuracy:**\n"
            for model_name, metrics in perf.items():
                result += f"• {model_name.replace('_', ' ').title()}: MAE ${metrics['mae']:.2f}\n"
        
        result += f"\n*⚠️ Disclaimer: This is a machine learning prediction based on historical data. Cryptocurrency markets are highly volatile and unpredictable. Not financial advice.*"
        
        logger.info(f"Successfully generated ML forecast for {coin}")
        return result
        
    except Exception as e:
        logger.error(f"Error in forecast_price: {str(e)}")
        return f"Error generating forecast: {str(e)}"

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
        Tool.from_function(
            name="forecast_price",
            func=forecast_price,
            description="Generate ML-based price forecasts for a cryptocurrency.",
        ),
    ]
    return tools
