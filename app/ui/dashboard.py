# app/ui/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db import engine

def show_dashboard():
    """Display the crypto dashboard with charts and metrics"""
    
    st.markdown("### 📊 Crypto Market Dashboard")
    
    try:
        # Get latest data
        with engine.connect() as conn:
            # Latest prices
            latest_query = text("""
                SELECT DISTINCT ON (coin_id) 
                    coin_id, symbol, price, date
                FROM prices 
                ORDER BY coin_id, date DESC
            """)
            latest_df = pd.read_sql(latest_query, conn)
            
            # Price history for charts
            history_query = text("""
                SELECT coin_id, symbol, price, date
                FROM prices 
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY coin_id, date
            """)
            history_df = pd.read_sql(history_query, conn)
        
        if latest_df.empty:
            st.warning("No data available. Please load some crypto data first.")
            return
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            btc_price = latest_df[latest_df['symbol'] == 'BITCOIN']['price'].iloc[0] if not latest_df[latest_df['symbol'] == 'BITCOIN'].empty else 0
            st.metric("Bitcoin (BTC)", f"${btc_price:,.2f}")
        
        with col2:
            eth_price = latest_df[latest_df['symbol'] == 'ETHEREUM']['price'].iloc[0] if not latest_df[latest_df['symbol'] == 'ETHEREUM'].empty else 0
            st.metric("Ethereum (ETH)", f"${eth_price:,.2f}")
        
        with col3:
            sol_price = latest_df[latest_df['symbol'] == 'SOLANA']['price'].iloc[0] if not latest_df[latest_df['symbol'] == 'SOLANA'].empty else 0
            st.metric("Solana (SOL)", f"${sol_price:,.2f}")
        
        st.markdown("---")
        
        # Price charts
        if not history_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Price Trends (30 Days)")
                fig = px.line(
                    history_df, 
                    x='date', 
                    y='price', 
                    color='symbol',
                    title="Cryptocurrency Price Trends",
                    labels={'price': 'Price (USD)', 'date': 'Date'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🥧 Market Share")
                # Create a simple market share pie chart based on latest prices
                fig_pie = px.pie(
                    latest_df, 
                    values='price', 
                    names='symbol',
                    title="Price Distribution"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Data table
        st.markdown("#### 📋 Latest Prices")
        display_df = latest_df.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"${x:,.2f}")
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        st.dataframe(
            display_df[['symbol', 'price', 'date']], 
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")

def show_analytics():
    """Show advanced analytics"""
    
    st.markdown("### 🔍 Advanced Analytics")
    
    try:
        with engine.connect() as conn:
            # Calculate price changes
            change_query = text("""
                WITH price_changes AS (
                    SELECT 
                        coin_id,
                        symbol,
                        price,
                        date,
                        LAG(price, 1) OVER (PARTITION BY coin_id ORDER BY date) as prev_price
                    FROM prices
                    WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                )
                SELECT 
                    symbol,
                    ROUND(AVG(price), 2) as avg_price,
                    ROUND(MIN(price), 2) as min_price,
                    ROUND(MAX(price), 2) as max_price,
                    ROUND(STDDEV(price), 2) as volatility,
                    COUNT(*) as data_points
                FROM price_changes
                WHERE prev_price IS NOT NULL
                GROUP BY symbol
                ORDER BY avg_price DESC
            """)
            
            analytics_df = pd.read_sql(change_query, conn)
        
        if not analytics_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Price Statistics")
                st.dataframe(analytics_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 📈 Volatility Analysis")
                fig_vol = px.bar(
                    analytics_df,
                    x='symbol',
                    y='volatility',
                    title="Price Volatility by Cryptocurrency",
                    labels={'volatility': 'Volatility (USD)', 'symbol': 'Cryptocurrency'}
                )
                st.plotly_chart(fig_vol, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading analytics: {e}")