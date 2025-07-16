# app/ui/health.py
"""Simple health check utilities for the Streamlit app"""

import streamlit as st
from sqlalchemy import text
from app.db import engine
import pandas as pd

def check_database_health():
    """Check if database is accessible and has data"""
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
            # Check if prices table exists and has data
            result = conn.execute(text("""
                SELECT COUNT(*) as total_records, 
                       COUNT(DISTINCT coin_id) as unique_coins,
                       MAX(date) as latest_date
                FROM prices
            """))
            stats = result.fetchone()
            
            return {
                "status": "healthy",
                "total_records": stats[0] if stats else 0,
                "unique_coins": stats[1] if stats else 0,
                "latest_date": stats[2] if stats else None
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def show_system_status():
    """Display system status in the sidebar"""
    health = check_database_health()
    
    if health["status"] == "healthy":
        st.success("🟢 System Healthy")
        if health["total_records"] > 0:
            st.info(f"📊 {health['total_records']} records | {health['unique_coins']} coins")
            if health["latest_date"]:
                st.info(f"📅 Latest: {health['latest_date']}")
        else:
            st.warning("⚠️ No data loaded yet")
    else:
        st.error("🔴 System Issues")
        st.error(f"Error: {health['error']}")
    
    return health